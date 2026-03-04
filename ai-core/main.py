from __future__ import annotations

from config import LLM_PROVIDER, VERTEX_CONFIG
from indexer import rebuild_index
from rag import RAGEngine, active_model_name, ask_llm, llm_available


def build_prompt(question: str, context: str) -> str:
    return f"""
Você é especialista em React, Next.js e arquitetura web.
Seu foco é sugerir código limpo, performático e offline-friendly.

Contexto do projeto:
{context}

Pergunta:
{question}

Responda com passos curtos e código otimizado.
""".strip()


def run() -> int:
    print("Mini Copilot Python (RAG local)")
    print(f"Provider LLM: {LLM_PROVIDER}")
    if LLM_PROVIDER == "vertex":
        print(f"Vertex auth mode: {VERTEX_CONFIG['auth_mode']}")
    print(f"Modelo configurado: {active_model_name()}")

    indexed_docs = rebuild_index()
    engine = RAGEngine()
    print(f"Índice carregado com {indexed_docs} chunks.")

    if not llm_available():
        if LLM_PROVIDER == "vertex":
            print(
                "Vertex indisponível. Configure: VERTEX_PROJECT_ID, VERTEX_LOCATION, "
                "VERTEX_MODEL e VERTEX_ACCESS_TOKEN"
            )
        else:
            print("Ollama indisponível. Inicie com: ollama serve")

    while True:
        try:
            question = input("\nPergunta (/exit para sair): ").strip()
        except EOFError:
            break

        if not question:
            continue
        if question == "/exit":
            break
        if question == "/reindex":
            indexed_docs = rebuild_index()
            engine.reload()
            print(f"Reindexado com {indexed_docs} chunks.")
            continue

        results = engine.search(question)
        context = engine.context_from_results(results)
        prompt = build_prompt(question, context)

        try:
            answer = ask_llm(prompt)
        except Exception as exc:  # noqa: BLE001
            print(f"Erro LLM: {exc}")
            continue

        print("\nResposta:\n")
        print(answer)

    print("Encerrado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
