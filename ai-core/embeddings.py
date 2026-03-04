from __future__ import annotations

import pickle
from typing import Iterable

import numpy as np

try:
    import faiss
except Exception:  # noqa: BLE001
    faiss = None

from config import DOCS_PATH, EMBEDDING_MODEL, INDEX_PATH, VECTOR_DIR

_model = None
_use_fallback_embeddings = True


class NumpyIndex:
    def __init__(self, vectors: np.ndarray | None = None) -> None:
        if vectors is None:
            self.vectors = np.zeros((0, 384), dtype="float32")
        else:
            self.vectors = np.asarray(vectors, dtype="float32")

    def add(self, vectors: np.ndarray) -> None:
        entries = np.asarray(vectors, dtype="float32")
        if entries.size == 0:
            return
        if self.vectors.size == 0:
            self.vectors = entries
            return
        self.vectors = np.vstack([self.vectors, entries])

    def search(self, query_vectors: np.ndarray, top_k: int) -> tuple[np.ndarray, np.ndarray]:
        query = np.asarray(query_vectors, dtype="float32")
        if query.ndim == 1:
            query = query.reshape(1, -1)

        if self.vectors.size == 0:
            distances = np.zeros((query.shape[0], top_k), dtype="float32")
            indices = np.full((query.shape[0], top_k), -1, dtype="int64")
            return distances, indices

        scores = np.matmul(query, self.vectors.T)
        max_k = min(top_k, self.vectors.shape[0])

        order = np.argsort(-scores, axis=1)
        selected = order[:, :max_k]
        selected_scores = np.take_along_axis(scores, selected, axis=1)

        if max_k < top_k:
            pad_size = top_k - max_k
            selected = np.pad(selected, ((0, 0), (0, pad_size)), constant_values=-1)
            selected_scores = np.pad(selected_scores, ((0, 0), (0, pad_size)), constant_values=0.0)

        return selected_scores.astype("float32"), selected.astype("int64")


def _fallback_embeddings(texts: list[str], dim: int = 384) -> np.ndarray:
    vectors = np.zeros((len(texts), dim), dtype="float32")
    for row_index, text in enumerate(texts):
        if not text:
            continue
        tokens = text.lower().split()
        for token in tokens:
            slot = hash(token) % dim
            vectors[row_index, slot] += 1.0

    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    vectors /= norms
    return vectors


def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def create_embeddings(texts: Iterable[str]) -> np.ndarray:
    global _use_fallback_embeddings

    entries = list(texts)
    if not entries:
        return np.zeros((0, 384), dtype="float32")

    if _use_fallback_embeddings:
        return _fallback_embeddings(entries)

    try:
        model = get_model()
        vectors = model.encode(
            entries,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return np.asarray(vectors, dtype="float32")
    except Exception:  # noqa: BLE001
        _use_fallback_embeddings = True
        return _fallback_embeddings(entries)


def save_index(vectors: np.ndarray, documents: list[dict]) -> None:
    VECTOR_DIR.mkdir(parents=True, exist_ok=True)

    if faiss is not None:
        if vectors.size == 0:
            dim = 384
            index = faiss.IndexFlatIP(dim)
        else:
            dim = vectors.shape[1]
            index = faiss.IndexFlatIP(dim)
            index.add(vectors)

        faiss.write_index(index, str(INDEX_PATH))
    else:
        np.save(str(INDEX_PATH.with_suffix(".npy")), np.asarray(vectors, dtype="float32"))

    with DOCS_PATH.open("wb") as handle:
        pickle.dump(documents, handle)


def load_index_and_docs() -> tuple[object, list[dict]]:
    docs: list[dict] = []
    if DOCS_PATH.exists():
        with DOCS_PATH.open("rb") as handle:
            docs = pickle.load(handle)

    if faiss is not None and INDEX_PATH.exists():
        index = faiss.read_index(str(INDEX_PATH))
        return index, docs

    npy_path = INDEX_PATH.with_suffix(".npy")
    if npy_path.exists():
        vectors = np.load(str(npy_path))
        return NumpyIndex(vectors), docs

    return NumpyIndex(), docs
