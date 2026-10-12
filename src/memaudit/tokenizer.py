"""Registered CPU tokenizer extracted without retrieval clients or model loading."""

from __future__ import annotations

import hashlib
import re
from typing import Any, Callable

ENGLISH_STOPWORDS: frozenset[str] = frozenset("""
i me my myself we our ours ourselves you your yours yourself yourselves he him his himself she her hers herself it its itself they
them their theirs themselves what which who whom this that these those am is are was were be been being have has had having do does
did doing a an the and but if or because as until while of at by for with about against between into through during before after
above below to from up down in out on off over under again further then once here there when where why how all any both each few
more most other some such no nor not only own same so than too very s t can will just don should now d ll m o re ve y ain aren
couldn didn doesn hadn hasn haven isn ma mightn mustn needn shan shouldn wasn weren won wouldn
""".split())

STOPWORDS_SHA256 = hashlib.sha256(" ".join(sorted(ENGLISH_STOPWORDS)).encode()).hexdigest()

_WORD = re.compile(r"[^\W_]+", re.UNICODE)

class Tokenizer:
    """Callable ``text -> list[str]``. See the module docstring for the two supported kinds."""

    def __init__(self, kind: str = "default", *, stopwords: bool = True, stem: bool = True, lowercase: bool = True, stemmer: str = "rust"):
        if kind not in ("default", "official_lme"):
            raise ValueError(f"unknown tokenizer kind {kind!r}")
        if stemmer not in ("rust", "snowball-py"):
            raise ValueError(f"stemmer must be 'rust' or 'snowball-py', got {stemmer!r}")
        self.kind = kind
        self.stopwords = stopwords and kind == "default"
        self.stem = stem and kind == "default"
        self.lowercase = lowercase and kind == "default"
        self.stemmer_name = stemmer
        self._stem_fn: Callable[[str], str] | None = None
        self._stem_cache: dict[str, str] = {}
        if self.stem:
            if stemmer == "rust":
                from py_rust_stemmers import SnowballStemmer
                self._stem_fn = SnowballStemmer("english").stem_word
            else:
                try:
                    import snowballstemmer
                except ImportError as exc:
                    raise RuntimeError("stemmer='snowball-py' needs the pure-python 'snowballstemmer' package (not installed)") from exc
                self._stem_fn = snowballstemmer.stemmer("english").stemWord

    def _stem(self, word: str) -> str:
        s = self._stem_cache.get(word)
        if s is None:
            s = self._stem_cache[word] = self._stem_fn(word)  # type: ignore[misc]
        return s

    def __call__(self, text: str) -> list[str]:
        if self.kind == "official_lme":
            return text.split(" ")
        toks = _WORD.findall(text.lower() if self.lowercase else text)
        if self.stopwords:
            toks = [t for t in toks if t not in ENGLISH_STOPWORDS]
        if self.stem:
            toks = [self._stem(t) for t in toks]
        return toks

    def describe(self) -> dict[str, Any]:
        d: dict[str, Any] = {"kind": self.kind, "lowercase": self.lowercase, "stopwords": self.stopwords, "stem": self.stem}
        if self.stopwords:
            d["stopwords_sha256"] = STOPWORDS_SHA256
            d["n_stopwords"] = len(ENGLISH_STOPWORDS)
        if self.stem:
            d["stemmer"] = self.stemmer_name
        return d
