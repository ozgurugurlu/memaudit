"""``FakeClient``: an offline, deterministic stand-in for any model (rehearsals, tests, replay plumbing).

The reply is a pure function of the request (and of ``draw_id``), so two runs give identical outputs and ledgers
up to timestamps. Plug in ``responder`` to script answers: it receives the :class:`Request` and returns a string.
"""
from __future__ import annotations

import json
from typing import Callable, Mapping, Sequence

from .base import LLMResult, Request, request_hash, sha256_hex


def _default_responder(req: Request) -> str:
    h = sha256_hex(f"{req.system or ''}\x1f{req.prompt}\x1f{req.draw_id or ''}")[:12]
    if req.json_schema is not None:
        return json.dumps({"fake": h})
    return f"fake-answer-{h}"


class FakeClient:
    name = "fake"
    provider = "fake"
    paid = False

    def __init__(self, responder: Callable[[Request], str] | None = None, *, model: str = "fake-model-v1",
                 fail_every: int | None = None):
        self.model = model
        self._responder = responder or _default_responder
        self._fail_every = fail_every
        self.n_calls = 0

    def complete(self, prompt: str, *, system: str | None = None, max_tokens: int = 1024, json_schema: Mapping | None = None,
                 tag: str = "", temperature: float | None = None, cache: str = "use", draw_id: str | None = None) -> LLMResult:
        req = Request(prompt, system, max_tokens, json_schema, tag, temperature, cache, draw_id)
        self.n_calls += 1
        rh = request_hash(self.provider, self.model, req)
        usage = {"input_tokens": len(prompt.split()) + len((system or "").split()), "output_tokens": 0,
                 "reasoning_tokens": 0, "cached_tokens": 0}
        if self._fail_every and self.n_calls % self._fail_every == 0:
            return LLMResult("", None, usage, 0.0, ok=False, error_code="fake_failure", model_reported=self.model, request_hash=rh)
        text = self._responder(req)
        words = text.split()
        if len(words) > max_tokens:
            text, finish = " ".join(words[:max_tokens]), "length"
        else:
            finish = "stop"
        usage["output_tokens"] = min(len(words), max_tokens)
        parsed = None
        if json_schema is not None:
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                return LLMResult(text, None, usage, 0.0, ok=False, error_code="json_error", model_reported=self.model,
                                 finish_reason=finish, request_hash=rh)
        return LLMResult(text, parsed, usage, 0.0, ok=True, model_reported=self.model, finish_reason=finish, request_hash=rh)

    def complete_many(self, requests: Sequence[Request], *, concurrency: int = 1) -> list[LLMResult]:
        return [self.complete(r.prompt, system=r.system, max_tokens=r.max_tokens, json_schema=r.json_schema, tag=r.tag,
                              temperature=r.temperature, cache=r.cache, draw_id=r.draw_id) for r in requests]
