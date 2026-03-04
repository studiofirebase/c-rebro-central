from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
VECTOR_DIR = BASE_DIR / "vector_db"
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
PROJECTS_DIR = BASE_DIR / "projects"

INDEX_PATH = VECTOR_DIR / "index.bin"
DOCS_PATH = VECTOR_DIR / "docs.pkl"
META_PATH = VECTOR_DIR / "meta.json"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").strip().lower()

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_TAGS_ENDPOINT = "http://localhost:11434/api/tags"

OLLAMA_CONFIG = {
    "model": os.getenv("OLLAMA_MODEL", "deepseek-coder:6.7b-instruct-q4_K_M"),
    "num_ctx": int(os.getenv("OLLAMA_NUM_CTX", "1024")),
    "num_thread": int(os.getenv("OLLAMA_NUM_THREAD", "4")),
    "temperature": float(os.getenv("OLLAMA_TEMPERATURE", "0.2")),
    "top_p": float(os.getenv("OLLAMA_TOP_P", "0.9")),
}

VERTEX_CONFIG = {
    "project_id": os.getenv("VERTEX_PROJECT_ID", ""),
    "location": os.getenv("VERTEX_LOCATION", "us-central1"),
    "model": os.getenv("VERTEX_MODEL", "gemini-1.5-flash"),
    "auth_mode": os.getenv("VERTEX_AUTH_MODE", "env").strip().lower(),
    "access_token": os.getenv("VERTEX_ACCESS_TOKEN", ""),
    "temperature": float(os.getenv("VERTEX_TEMPERATURE", "0.2")),
    "top_p": float(os.getenv("VERTEX_TOP_P", "0.9")),
    "top_k": int(os.getenv("VERTEX_TOP_K", "40")),
    "candidate_count": int(os.getenv("VERTEX_CANDIDATE_COUNT", "1")),
    "max_output_tokens": int(os.getenv("VERTEX_MAX_OUTPUT_TOKENS", "1024")),
    "timeout_seconds": int(os.getenv("VERTEX_TIMEOUT_SECONDS", "90")),
    "max_retries": int(os.getenv("VERTEX_MAX_RETRIES", "3")),
    "retry_base_seconds": float(os.getenv("VERTEX_RETRY_BASE_SECONDS", "1.2")),
    "retry_max_seconds": float(os.getenv("VERTEX_RETRY_MAX_SECONDS", "8")),
    "system_instruction": os.getenv("VERTEX_SYSTEM_INSTRUCTION", ""),
    "safety_hate": os.getenv("VERTEX_SAFETY_HATE", "BLOCK_MEDIUM_AND_ABOVE"),
    "safety_harassment": os.getenv("VERTEX_SAFETY_HARASSMENT", "BLOCK_MEDIUM_AND_ABOVE"),
    "safety_sexual": os.getenv("VERTEX_SAFETY_SEXUAL", "BLOCK_MEDIUM_AND_ABOVE"),
    "safety_dangerous": os.getenv("VERTEX_SAFETY_DANGEROUS", "BLOCK_MEDIUM_AND_ABOVE"),
}

INDEXING_CONFIG = {
    "chunk_size": 1200,
    "chunk_overlap": 150,
    "top_k": 3,
    "watch_debounce_seconds": 1.0,
}

IGNORED_DIRS = {
    "node_modules",
    ".next",
    "dist",
    "build",
    ".git",
    "public",
    "coverage",
    "__pycache__",
    "venv",
    ".venv",
}

ALLOWED_EXT = {".js", ".ts", ".tsx", ".jsx", ".py", ".md", ".json"}
