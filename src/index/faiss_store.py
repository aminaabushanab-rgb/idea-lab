import os, json
from typing import List, Dict, Optional
import numpy as np
import faiss
from sklearn.preprocessing import normalize
import yaml
from langchain_community.embeddings import HuggingFaceEmbeddings
from src.config import CONFIG
from langchain_huggingface import HuggingFaceEmbeddings

with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

class FAISSStore:
    """
    Minimal FAISS wrapper using local HuggingFace embeddings.
    - Cosine similarity (via inner product on L2-normalized vectors)
    - Saves/loads index + metadata
    """

    def __init__(self, dirpath: str = "data/index"):
        os.makedirs(dirpath, exist_ok=True)
        self.dir = dirpath
        self.index: Optional[faiss.Index] = None
        self.meta: List[Dict] = []
        # One embedding model instance reused for speed
        self._emb = HuggingFaceEmbeddings(model_name=CONFIG["embed_model"])

    # ---- internal helpers ----
    @staticmethod
    def _l2_normalize(X: np.ndarray) -> np.ndarray:
        return normalize(X, axis=1)

    # ---- build / add ----
    def build(self, texts: List[str], meta: Optional[List[Dict]] = None) -> None:
        if not texts:
            raise ValueError("No texts provided to build().")
        if meta is not None and len(texts) != len(meta):
            raise ValueError("texts and meta must have the same length.")

        vecs = np.asarray(self._emb.embed_documents(texts), dtype="float32")
        vecs = self._l2_normalize(vecs)
        dim = vecs.shape[1]

        # Inner-product index; with normalized vectors this equals cosine similarity
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(vecs)

        if meta is None:
            self.meta = [{"id": i, "text": t} for i, t in enumerate(texts)]
        else:
            self.meta = [{"id": i, "text": t, "meta": m} for i, (t, m) in enumerate(zip(texts, meta))]

    def add(self, texts: List[str], meta: Optional[List[Dict]] = None) -> None:
        if self.index is None:
            return self.build(texts, meta)

        vecs = np.asarray(self._emb.embed_documents(texts), dtype="float32")
        vecs = self._l2_normalize(vecs)
        self.index.add(vecs)

        start = len(self.meta)
        if meta is None:
            self.meta.extend([{"id": start + i, "text": t} for i, t in enumerate(texts)])
        else:
            self.meta.extend(
                [{"id": start + i, "text": t, "meta": m} for i, (t, m) in enumerate(zip(texts, meta))]
            )

    # ---- persistence ----
    def save(self) -> None:
        if self.index is None:
            raise RuntimeError("No index to save. Call build() first.")
        faiss.write_index(self.index, os.path.join(self.dir, "store.faiss"))
        with open(os.path.join(self.dir, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(self.meta, f, ensure_ascii=False)

    def load(self) -> None:
        self.index = faiss.read_index(os.path.join(self.dir, "store.faiss"))
        with open(os.path.join(self.dir, "meta.json"), encoding="utf-8") as f:
            self.meta = json.load(f)

    # ---- search ----
    def search(self, query: str, k: int = 5) -> List[Dict]:
        if self.index is None:
            raise RuntimeError("Index not loaded. Call load() or build() first.")

        q = np.asarray([self._emb.embed_query(query)], dtype="float32")
        q = self._l2_normalize(q)
        scores, ids = self.index.search(q, k)

        results: List[Dict] = []
        for idx, score in zip(ids[0].tolist(), scores[0].tolist()):
            if idx == -1:
                continue
            item = dict(self.meta[idx])  # copy
            item["score"] = float(score)  # cosine similarity in [-1, 1]
            results.append(item)
        return results

