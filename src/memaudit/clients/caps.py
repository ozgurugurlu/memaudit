"""Call and spend caps enforced from the ledger.

:class:`CappedClient` wraps any :class:`~memaudit.clients.base.LLMClient`. Every call is checked *before* it is sent:

* ``max_calls`` (required): live attempts of this ``run_id`` in the ledger (cache hits do not count);
* ``cap_usd`` (required when the wrapped client is ``paid``): USD of this run's ledger rows at a user-supplied
  :class:`PriceTable`, plus a worst-case estimate of the next call, must stay within the cap.

memaudit ships the price-table *format*, not prices: the user supplies the prices of the provider they use.
A refused call writes a ``refused_cap`` row and raises; nothing is sent.
"""
from __future__ import annotations

import math
import json
import os
from pathlib import Path
import time
import uuid
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .base import LLMClient, LLMResult, Request, request_hash, sha256_hex
from .ledger import JsonlLedger, live_attempts, make_row
from ..lock import FileLock


class CapExceeded(RuntimeError):
    pass


class CallCapExceeded(CapExceeded):
    pass


class SpendCapExceeded(CapExceeded):
    pass


class PriceMissing(KeyError):
    pass


@dataclass(frozen=True)
class Price:
    input_per_mtok: float          # USD per million input tokens
    output_per_mtok: float         # USD per million output tokens (reasoning tokens are billed as output)
    cached_input_per_mtok: float | None = None


class PriceTable:
    """``{model_id: Price}``. Lookups of an unknown model raise (never a silent zero)."""

    def __init__(self, prices: Mapping[str, Price]):
        for m, p in prices.items():
            for v in (p.input_per_mtok, p.output_per_mtok, p.cached_input_per_mtok):
                if v is not None and (not math.isfinite(v) or v < 0):
                    raise ValueError(f"invalid price for {m!r}")
        self._prices = dict(prices)

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Mapping[str, float]]) -> "PriceTable":
        return cls({m: Price(float(v["input_per_mtok"]), float(v["output_per_mtok"]),
                             None if v.get("cached_input_per_mtok") is None else float(v["cached_input_per_mtok"]))
                    for m, v in raw.items()})

    def price(self, model: str) -> Price:
        try:
            return self._prices[model]
        except KeyError:
            raise PriceMissing(f"no price for model {model!r}; add it to the price table") from None

    def row_usd(self, row: Mapping[str, Any]) -> float:
        if row.get("status") in ("cache_hit", "refused_cap"):
            return 0.0
        if row.get("billing_unknown"):
            raise SpendCapExceeded("unknown synthetic billing prevents further budgeted calls")
        if any(type(row.get(k)) is not int or row[k] < 0 for k in ("input_tokens", "output_tokens")):
            raise SpendCapExceeded("missing or invalid usage prevents further budgeted calls")
        p = self.price(str(row.get("model_requested")))
        inp = int(row.get("input_tokens") or 0)
        cached = int(row.get("cached_tokens") or 0)
        out = int(row.get("output_tokens") or 0)          # output includes reasoning tokens by convention
        if min(inp, cached, out) < 0 or cached > inp:
            raise ValueError("invalid token counts")
        cached_price = p.input_per_mtok if p.cached_input_per_mtok is None else p.cached_input_per_mtok
        return ((inp - cached) * p.input_per_mtok + cached * cached_price + out * p.output_per_mtok) / 1e6

    def rows_usd(self, rows: Sequence[Mapping[str, Any]]) -> float:
        return float(sum(self.row_usd(r) for r in rows))


def worst_case_usd(price: Price, req: Request) -> float:
    """Upper bound for one call: every UTF-8 byte of the prompt counted as an input token, ``max_tokens`` output."""
    n_in = len(req.prompt.encode("utf-8")) + len((req.system or "").encode("utf-8"))
    return (n_in * price.input_per_mtok + req.max_tokens * price.output_per_mtok) / 1e6


class CappedClient:
    """Ledgered, capped wrapper. ``run_id`` scopes the caps (default: a fresh uuid per wrapper)."""

    def __init__(self, inner: LLMClient, *, ledger: JsonlLedger, max_calls: int, cap_usd: float | None = None,
                 prices: PriceTable | None = None, run_id: str | None = None):
        if type(max_calls) is not int or max_calls < 0:
            raise ValueError("max_calls is required and must be a non-negative integer")
        if getattr(inner, "paid", True):
            if cap_usd is None or prices is None:
                raise ValueError(f"client {inner.name!r} is paid: cap_usd and a price table are required")
            prices.price(inner.model)                       # fail now, not at the first call
        if cap_usd is not None and (type(cap_usd) not in (int, float) or not math.isfinite(cap_usd) or cap_usd < 0):
            raise ValueError("cap_usd must be a finite non-negative number")
        self.inner, self.ledger, self.max_calls, self.cap_usd, self.prices = inner, ledger, max_calls, cap_usd, prices
        self.run_id = run_id or uuid.uuid4().hex
        self.name, self.provider, self.model, self.paid = inner.name, inner.provider, inner.model, inner.paid
        self._pending_path = Path(str(ledger.path)+".pending")

    # ------------------------------------------------------------------ accounting
    def rows(self) -> list[dict]:
        rows = self.ledger.rows_for(run_id=self.run_id)
        if self._pending_path.exists():
            pending = json.loads(self._pending_path.read_text())
            if pending["run_id"] == self.run_id and not any(r.get("attempt_id") == pending["attempt_id"] for r in rows):
                rows.append(pending)
        return rows

    def _reconcile_pending(self):
        if not self._pending_path.exists(): return
        pending = json.loads(self._pending_path.read_text())
        if not any(r.get("attempt_id") == pending["attempt_id"] for r in self.ledger.read()):
            self.ledger.append(pending)
        self._pending_path.unlink()

    def _reserve(self, row):
        self._pending_path.parent.mkdir(parents=True, exist_ok=True)
        temp = Path(str(self._pending_path)+".tmp")
        with temp.open("w", encoding="utf-8") as f:
            json.dump(row, f); f.flush(); os.fsync(f.fileno())
        os.replace(temp, self._pending_path)

    def calls_used(self) -> int:
        return live_attempts(self.rows())

    def spend_usd(self) -> float:
        return self.prices.rows_usd(self.rows()) if self.prices is not None else 0.0

    def _base_row(self, req: Request, rh: str) -> dict:
        return {"run_id": self.run_id, "client": self.name, "provider": self.provider, "model_requested": self.model,
                "request_hash": rh, "prompt_sha256": sha256_hex(req.prompt), "tag": req.tag, "attempt": 1,
                "max_tokens": req.max_tokens, "temperature": req.temperature, "draw_id": req.draw_id}

    def _check(self, req: Request, rh: str) -> None:
        used = self.calls_used()
        if used >= self.max_calls:
            self.ledger.append(make_row(**self._base_row(req, rh), status="refused_cap", ok=False, error_code="max_calls"))
            raise CallCapExceeded(f"run {self.run_id}: {used} of max_calls={self.max_calls} used")
        if self.cap_usd is not None and self.prices is not None:
            spent = self.spend_usd()
            nxt = worst_case_usd(self.prices.price(self.model), req)
            if spent + nxt > self.cap_usd:
                self.ledger.append(make_row(**self._base_row(req, rh), status="refused_cap", ok=False, error_code="cap_usd"))
                raise SpendCapExceeded(f"run {self.run_id}: spent {spent:.4f} + worst case {nxt:.4f} > cap {self.cap_usd:.4f} USD")

    # ------------------------------------------------------------------ protocol
    def complete(self, prompt: str, *, system: str | None = None, max_tokens: int = 1024, json_schema=None, tag: str = "",
                 temperature: float | None = None, cache: str = "use", draw_id: str | None = None) -> LLMResult:
        # Serialize the check/call/append transaction across wrappers sharing this ledger.
        with FileLock(str(self.ledger.path) + ".caps.lock", timeout_s=60):
            return self._complete_locked(prompt, system=system, max_tokens=max_tokens, json_schema=json_schema, tag=tag,
                                         temperature=temperature, cache=cache, draw_id=draw_id)

    def _complete_locked(self, prompt: str, *, system=None, max_tokens=1024, json_schema=None, tag="",
                         temperature=None, cache="use", draw_id=None) -> LLMResult:
        if type(max_tokens) is not int or max_tokens < 1 or cache not in ("use", "bypass", "refresh", "only"):
            raise ValueError("invalid request limits or cache mode")
        if temperature is not None and (type(temperature) not in (int, float) or not math.isfinite(temperature) or temperature < 0):
            raise ValueError("invalid temperature")
        req = Request(prompt, system, max_tokens, json_schema, tag, temperature, cache, draw_id)
        rh = request_hash(self.provider, self.model, req)
        self._reconcile_pending()
        make_row(**self._base_row(req, rh), status="ok")  # validate metadata before dispatch
        self._check(req, rh)
        attempt_id = uuid.uuid4().hex
        self._reserve(make_row(**self._base_row(req, rh), attempt_id=attempt_id, status="network_error", ok=False,
                               error_code="interrupted_attempt", billing_unknown=bool(self.paid)))
        t0 = time.monotonic()
        try:
            res = self.inner.complete(prompt, system=system, max_tokens=max_tokens, json_schema=json_schema, tag=tag,
                                      temperature=temperature, cache=cache, draw_id=draw_id)
        except Exception:
            self.ledger.append(make_row(**self._base_row(req, rh), attempt_id=attempt_id, status="network_error", ok=False,
                                        error_code="client_exception", billing_unknown=bool(self.paid)))
            self._pending_path.unlink()
            raise RuntimeError("client attempt failed; sanitized failure recorded") from None
        if not isinstance(res, LLMResult) or type(res.cached) is not bool or type(res.ok) is not bool:
            self.ledger.append(make_row(**self._base_row(req, rh), attempt_id=attempt_id, status="invalid_response", ok=False,
                                        cached=False, error_code="invalid_result_flags", billing_unknown=bool(self.paid)))
            self._pending_path.unlink()
            raise RuntimeError("invalid client result; sanitized failure recorded")
        usage = res.usage if isinstance(res.usage, Mapping) else {}
        token_fields = ("input_tokens", "output_tokens", "reasoning_tokens", "cached_tokens")
        u = {k: v if type(v := usage.get(k)) is int and v >= 0 else None for k in token_fields}
        usage_complete = all(u[k] is not None for k in ("input_tokens", "output_tokens"))
        usage_complete &= all(usage.get(k) is None or u[k] is not None for k in token_fields)
        if u["cached_tokens"] is not None and (u["input_tokens"] is None or u["cached_tokens"] > u["input_tokens"]):
            u["cached_tokens"] = None
            usage_complete = False
        # A response is not evidence of known spend: both primary usage counts
        # must be valid. Unknown paid billing fails closed on the next attempt.
        billing_unknown = bool(self.paid and not res.cached and not usage_complete)
        self.ledger.append(make_row(
            **self._base_row(req, rh), attempt_id=attempt_id, status="cache_hit" if res.cached else ("ok" if res.ok else "invalid_response"),
            ok=bool(res.ok), error_code=res.error_code, cached=bool(res.cached), billing_unknown=billing_unknown,
            model_reported=res.model_reported, finish_reason=res.finish_reason,
            input_tokens=u.get("input_tokens"), output_tokens=u.get("output_tokens"), reasoning_tokens=u.get("reasoning_tokens"),
            cached_tokens=u.get("cached_tokens"), network_ms=res.latency_ms or 1000.0 * (time.monotonic() - t0), queue_ms=0.0))
        self._pending_path.unlink()
        res.request_hash = rh
        return res

    def complete_many(self, requests: Sequence[Request], *, concurrency: int = 1) -> list[LLMResult]:
        """Sequential in v0.1 (caps are checked per call; concurrency is accepted for protocol compatibility)."""
        return [self.complete(r.prompt, system=r.system, max_tokens=r.max_tokens, json_schema=r.json_schema, tag=r.tag,
                              temperature=r.temperature, cache=r.cache, draw_id=r.draw_id) for r in requests]
