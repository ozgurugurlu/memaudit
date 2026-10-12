"""Minimal, provider-neutral client protocol.

Every model call in memaudit goes through an object that satisfies :class:`LLMClient`. v0.1 ships only
:class:`~memaudit.clients.fake.FakeClient` (offline, deterministic) and the :class:`~memaudit.clients.caps.CappedClient`
wrapper (ledger + call / USD caps). Real provider clients (an OpenAI-compatible HTTP client, optionally Gemini) are
v0.2 work; they must implement this protocol and set ``paid`` honestly.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence, runtime_checkable


@dataclass
class LLMResult:
    text: str                                   # assistant text ('' on failure); never written to the ledger
    parsed: Any | None = None                   # parsed JSON when ``json_schema`` was given and parsing succeeded
    usage: dict = field(default_factory=dict)   # input_tokens, output_tokens, reasoning_tokens?, cached_tokens?
    latency_ms: float = 0.0                     # network / compute time of this call
    cached: bool = False                        # served from a cache (no spend)
    ok: bool = True
    error_code: str | None = None               # short enum-like code only; no server text
    model_reported: str | None = None
    finish_reason: str | None = None
    request_hash: str = ""


@dataclass(frozen=True)
class Request:
    """One completion request (the unit of ``complete_many``)."""
    prompt: str
    system: str | None = None
    max_tokens: int = 1024
    json_schema: Mapping[str, Any] | None = None
    tag: str = ""
    temperature: float | None = None
    cache: str = "use"                          # 'use' | 'bypass' | 'refresh' | 'only'
    draw_id: str | None = None                  # forces a distinct request (fresh sample) when a backend replays identical bodies


CACHE_MODES = ("use", "bypass", "refresh", "only")


@runtime_checkable
class LLMClient(Protocol):
    name: str          # client label, e.g. 'fake' or 'openai-compat'
    provider: str      # e.g. 'fake', 'openai-compat'
    model: str         # model id as requested
    paid: bool         # True if a call can cost money (then a USD cap is mandatory)

    def complete(self, prompt: str, *, system: str | None = None, max_tokens: int = 1024,
                 json_schema: Mapping[str, Any] | None = None, tag: str = "", temperature: float | None = None,
                 cache: str = "use", draw_id: str | None = None) -> LLMResult: ...

    def complete_many(self, requests: Sequence[Request], *, concurrency: int = 1) -> list[LLMResult]: ...


def canonical_json(obj: Any) -> str:
    """Deterministic compact JSON (insertion order kept; NaN / Inf rejected)."""
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def sha256_hex(data: str | bytes) -> str:
    return hashlib.sha256(data.encode("utf-8") if isinstance(data, str) else data).hexdigest()


def request_hash(provider: str, model: str, req: Request) -> str:
    """sha256 over everything that defines a request (prompt, system, limits, schema, temperature, draw id)."""
    body = {"provider": provider, "model": model, "prompt": req.prompt, "system": req.system, "max_tokens": req.max_tokens,
            "json_schema": req.json_schema, "temperature": req.temperature, "draw_id": req.draw_id}
    return sha256_hex(canonical_json(body))
