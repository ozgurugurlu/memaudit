"""Optional dense encoder for the hybrid wrong-question retriever (``pip install 'memaudit[hybrid]'``).

BM25 is the default retriever and needs nothing from this module.  The hybrid configuration ``S16_HYBRID`` is the
retriever stack of the S16 wrong-question atlas: BM25 Okapi (k1 1.5, b 0.75, registered tokenizer) plus
bge-small-en-v1.5 (FastEmbed int8 ONNX export), fused per turn by reciprocal-rank fusion (c = 60, average-rank ties),
scored on user-side F1-normalised turns and max-pooled per unit.

FastEmbed is imported only when a dense encoder is constructed.  If it is not importable, ``OptionalDependencyError``
is raised with a fixed message; the BM25 path never imports it.  The encoder never downloads: the caller passes a local
model directory, ``HF_HUB_OFFLINE=1`` is set before the import, and ``local_files_only=True`` is passed.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Protocol, Sequence

import numpy as np

S16_HYBRID = {
    "name": "s16-hybrid",
    "lexical": "BM25 Okapi k1=1.5 b=0.75 over turns; registered tokenizer (default, rust stemmer)",
    "dense_model": "BAAI/bge-small-en-v1.5",
    "dense_export": "Qdrant/bge-small-en-v1.5-onnx-Q (int8 ONNX)",
    "dense_snapshot_revision": "aa8f8b060edb00e03bfdd08813a2949946c8ba55",
    "fastembed_version": "0.8.1",
    "embedding_dim": 384,
    "query_prefix": "Represent this sentence for searching relevant passages: ",
    "doc_prefix": "",
    "fusion": "per-turn reciprocal-rank fusion, c=60, average-rank ties",
    "text": "user-side turns after F1 typography normalisation",
    "pooling": "maximum turn score per unit",
    "encode_order": "distinct prefixed texts sorted by (length, sha256), batches of 32",
    "threads": 1,
}
FASTEMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"
RRF_C = 60
ENCODE_BATCH = 32


class OptionalDependencyError(RuntimeError):
    """An optional extra is not installed.  The message is fixed and never contains input text or paths."""


MISSING_FASTEMBED = ("the hybrid retriever needs the optional 'hybrid' extra (fastembed) and a local model directory; "
                     "install it with: pip install 'memaudit[hybrid]'")


def fastembed_available() -> bool:
    try:
        import fastembed  # noqa: F401
    except ImportError:
        return False
    return True


def require_fastembed():
    """Import FastEmbed or raise ``OptionalDependencyError``; never downloads anything."""
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    try:
        import fastembed
    except ImportError as exc:  # ModuleNotFoundError included
        raise OptionalDependencyError(MISSING_FASTEMBED) from exc
    return fastembed


class Encoder(Protocol):
    """Anything that maps texts (already prefixed) to an (n, d) array."""

    def embed(self, texts: Sequence[str]) -> np.ndarray: ...


def normalise(raw) -> np.ndarray:
    v = np.asarray(raw)
    if v.ndim != 2 or v.dtype.kind not in "iuf":
        raise ValueError("encoder returned an invalid embedding array")
    v = v.astype(np.float32)
    if not np.isfinite(v).all():
        raise ValueError("encoder returned non-finite values")
    norms = np.linalg.norm(v, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return (v / norms).astype(np.float32)


def pass_order(strings: Sequence[str]) -> list[str]:
    """Distinct strings sorted by (length, sha256): the S16 encode order."""
    return sorted(set(strings), key=lambda s: (len(s), hashlib.sha256(s.encode("utf-8")).hexdigest()))


class VectorCache:
    """In-memory vectors keyed by sha256(prefix + text); nothing is persisted."""

    def __init__(self, encoder: Encoder, *, batch: int = ENCODE_BATCH):
        if type(batch) is not int or batch < 1:
            raise ValueError("batch must be a positive integer")
        self.encoder, self.batch = encoder, batch
        self._vec: dict[bytes, np.ndarray] = {}
        self.dim: int | None = None
        self.n_encoded = 0

    @staticmethod
    def key(prefix: str, text: str) -> bytes:
        return hashlib.sha256((prefix + text).encode("utf-8")).digest()

    def encode_pass(self, texts: Sequence[str], prefix: str) -> None:
        """Encode every missing prefixed text in fixed batches over the full sorted list (first write wins)."""
        strings = pass_order([prefix + t for t in texts])
        keys = [hashlib.sha256(s.encode("utf-8")).digest() for s in strings]
        for i in range(0, len(strings), self.batch):
            bk = keys[i:i + self.batch]
            if all(k in self._vec for k in bk):
                continue
            vecs = normalise(self.encoder.embed(strings[i:i + self.batch]))
            if vecs.shape[0] != len(bk) or (self.dim is not None and vecs.shape[1] != self.dim):
                raise ValueError("encoder returned the wrong number of rows or width")
            self.dim = int(vecs.shape[1])
            for j, k in enumerate(bk):
                if k not in self._vec:
                    self._vec[k] = vecs[j]
                    self.n_encoded += 1

    def vectors(self, texts: Sequence[str], prefix: str) -> np.ndarray:
        missing = [t for t in texts if self.key(prefix, t) not in self._vec]
        if missing:
            self.encode_pass(missing, prefix)
        if not texts:
            return np.zeros((0, self.dim or 0), dtype=np.float32)
        return np.stack([self._vec[self.key(prefix, t)] for t in texts]).astype(np.float32)


class FastEmbedEncoder:
    """Local FastEmbed CPU model; loaded lazily from ``model_path``; never downloads."""

    def __init__(self, model_path: str | os.PathLike, *, model_name: str = FASTEMBED_MODEL_NAME, threads: int = 1):
        if type(threads) is not int or threads < 1:
            raise ValueError("threads must be a positive integer")
        self.fastembed = require_fastembed()
        self.model_path = Path(model_path)
        if not self.model_path.is_dir():
            raise ValueError("the local model directory does not exist")
        self.model_name, self.threads = model_name, threads
        self._m = None

    def _load(self):
        if self._m is None:
            self._m = self.fastembed.TextEmbedding(self.model_name, specific_model_path=str(self.model_path),
                                                   local_files_only=True, threads=self.threads,
                                                   providers=["CPUExecutionProvider"], lazy_load=False)
        return self._m

    def embed(self, texts: Sequence[str]) -> np.ndarray:
        m = self._load()
        return np.asarray(list(m.embed(list(texts), batch_size=max(1, len(texts)), parallel=None)))

    def describe(self) -> dict:
        files = {}
        for name in ("model_optimized.onnx", "model.onnx", "tokenizer.json", "config.json"):
            p = self.model_path / name
            if p.is_file():
                h = hashlib.sha256()
                with p.open("rb") as f:
                    for block in iter(lambda: f.read(1 << 20), b""):
                        h.update(block)
                files[name] = h.hexdigest()
        return {"backend": "fastembed", "fastembed_version": getattr(self.fastembed, "__version__", None),
                "model_name": self.model_name, "threads": self.threads, "model_files_sha256": files,
                "matches_s16_fastembed_version": getattr(self.fastembed, "__version__", None) == S16_HYBRID["fastembed_version"]}
