from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.error
import urllib.request

import numpy as np

from config import (
    INDEXING_CONFIG,
    LLM_PROVIDER,
    OLLAMA_CONFIG,
    OLLAMA_ENDPOINT,
    OLLAMA_TAGS_ENDPOINT,
    VERTEX_CONFIG,
)
from embeddings import create_embeddings, load_index_and_docs


class RAGEngine:
    def __init__(self) -> None:
        self.index, self.documents = load_index_and_docs()

    def reload(self) -> None:
        self.index, self.documents = load_index_and_docs()

    def search(self, query: str, k: int | None = None) -> list[dict]:
        top_k = k or INDEXING_CONFIG["top_k"]
        query_vector = create_embeddings([query])
        if query_vector.size == 0:
            return []

        distances, indices = self.index.search(np.asarray(query_vector, dtype="float32"), top_k)

        results: list[dict] = []
        for score, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.documents):
                continue
            row = dict(self.documents[idx])
            row["score"] = float(score)
            results.append(row)
        return results

    def context_from_results(self, results: list[dict]) -> str:
        if not results:
            return ""
        return "\n\n".join(
            f"[source: {item['path']} chunk:{item['chunk']} score:{item['score']:.4f}]\n{item['content']}"
            for item in results
        )


def ollama_available() -> bool:
    try:
        req = urllib.request.Request(OLLAMA_TAGS_ENDPOINT, method="GET")
        with urllib.request.urlopen(req, timeout=2) as response:
            return response.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def vertex_available() -> bool:
    required = [
        _resolve_vertex_project_id(allow_gcloud=False),
        VERTEX_CONFIG["location"],
        VERTEX_CONFIG["model"],
    ]
    return all(bool(value) for value in required)


def llm_available() -> bool:
    if LLM_PROVIDER == "vertex":
        return vertex_available()
    return ollama_available()


def active_model_name() -> str:
    if LLM_PROVIDER == "vertex":
        return VERTEX_CONFIG["model"]
    return OLLAMA_CONFIG["model"]


def _resolve_vertex_access_token() -> str:
    token = VERTEX_CONFIG["access_token"].strip()
    auth_mode = VERTEX_CONFIG["auth_mode"]

    if auth_mode in {"env", "auto"} and token:
        return token

    if auth_mode in {"gcloud", "auto"}:
        try:
            completed = subprocess.run(
                ["gcloud", "auth", "application-default", "print-access-token"],
                capture_output=True,
                check=False,
                text=True,
                timeout=8,
            )
            maybe_token = completed.stdout.strip()
            if completed.returncode == 0 and maybe_token:
                return maybe_token
        except Exception:
            return ""

    return ""


def _resolve_vertex_project_id(allow_gcloud: bool = True) -> str:
    from_env = os.getenv("GOOGLE_CLOUD_PROJECT", "").strip()
    if from_env:
        return from_env

    project_id = VERTEX_CONFIG["project_id"].strip()
    if project_id:
        return project_id

    if not allow_gcloud:
        return ""

    try:
        completed = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True,
            check=False,
            text=True,
            timeout=5,
        )
        value = completed.stdout.strip()
        if completed.returncode == 0 and value and value != "(unset)":
            return value
    except Exception:
        return ""

    return ""


def _ask_ollama(prompt: str) -> str:
    payload = {
        **OLLAMA_CONFIG,
        "prompt": prompt,
        "stream": False,
    }

    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        OLLAMA_ENDPOINT,
        method="POST",
        headers={"Content-Type": "application/json"},
        data=data,
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read().decode("utf-8")
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("Falha ao acessar Ollama local.") from exc

    parsed = json.loads(raw)
    answer = (parsed.get("response") or "").strip()
    if not answer:
        raise RuntimeError("Resposta inválida do Ollama.")
    return answer


def _ask_vertex(prompt: str) -> str:
    project_id = _resolve_vertex_project_id(allow_gcloud=True)
    access_token = _resolve_vertex_access_token()
    if not project_id or not access_token:
        raise RuntimeError(
            "Vertex não configurado. Defina VERTEX_PROJECT_ID, VERTEX_LOCATION, "
            "VERTEX_MODEL e VERTEX_ACCESS_TOKEN, ou use VERTEX_AUTH_MODE=gcloud."
        )

    endpoint = (
        "https://"
        f"{VERTEX_CONFIG['location']}-aiplatform.googleapis.com/v1/projects/"
        f"{project_id}/locations/{VERTEX_CONFIG['location']}/"
        f"publishers/google/models/{VERTEX_CONFIG['model']}:generateContent"
    )

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {
            "temperature": VERTEX_CONFIG["temperature"],
            "topP": VERTEX_CONFIG["top_p"],
            "topK": VERTEX_CONFIG["top_k"],
            "candidateCount": VERTEX_CONFIG["candidate_count"],
            "maxOutputTokens": VERTEX_CONFIG["max_output_tokens"],
        },
        "safetySettings": [
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": VERTEX_CONFIG["safety_hate"],
            },
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": VERTEX_CONFIG["safety_harassment"],
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": VERTEX_CONFIG["safety_sexual"],
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": VERTEX_CONFIG["safety_dangerous"],
            },
        ],
    }

    if VERTEX_CONFIG["system_instruction"].strip():
        payload["systemInstruction"] = {
            "parts": [{"text": VERTEX_CONFIG["system_instruction"].strip()}]
        }

    last_error: Exception | None = None
    max_retries = max(1, VERTEX_CONFIG["max_retries"])

    for attempt in range(1, max_retries + 1):
        request = urllib.request.Request(
            endpoint,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
            data=json.dumps(payload).encode("utf-8"),
        )

        try:
            with urllib.request.urlopen(request, timeout=VERTEX_CONFIG["timeout_seconds"]) as response:
                raw = response.read().decode("utf-8")
                break
        except urllib.error.HTTPError as exc:
            status = getattr(exc, "code", 0)
            details = exc.read().decode("utf-8", errors="ignore") if hasattr(exc, "read") else ""
            last_error = RuntimeError(f"Falha no Vertex endpoint ({status}): {details or exc}")

            retryable = status in {429, 500, 502, 503, 504}
            if attempt >= max_retries or not retryable:
                raise last_error from exc

            backoff = min(
                VERTEX_CONFIG["retry_max_seconds"],
                VERTEX_CONFIG["retry_base_seconds"] * (2 ** (attempt - 1)),
            )
            time.sleep(backoff)
        except Exception as exc:  # noqa: BLE001
            last_error = RuntimeError("Falha ao acessar Vertex endpoint.")
            if attempt >= max_retries:
                raise last_error from exc
            backoff = min(
                VERTEX_CONFIG["retry_max_seconds"],
                VERTEX_CONFIG["retry_base_seconds"] * (2 ** (attempt - 1)),
            )
            time.sleep(backoff)
    else:
        raise RuntimeError(f"Falha ao acessar Vertex endpoint: {last_error}")

    parsed = json.loads(raw)
    candidates = parsed.get("candidates") or []
    if not candidates:
        raise RuntimeError("Resposta inválida do Vertex.")

    parts = ((candidates[0].get("content") or {}).get("parts") or [])
    text_parts = [part.get("text", "") for part in parts if isinstance(part, dict)]
    answer = "".join(text_parts).strip()
    if not answer:
        raise RuntimeError("Resposta vazia do Vertex.")
    return answer


def ask_llm(prompt: str) -> str:
    if LLM_PROVIDER == "vertex":
        return _ask_vertex(prompt)
    return _ask_ollama(prompt)
