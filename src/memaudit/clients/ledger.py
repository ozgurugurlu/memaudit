"""Append-only JSONL call ledger, schema ``memaudit-ledger/1``.

One row per call attempt and per cache hit. Rows hold identifiers, hashes, token counts and timings: **never** a
prompt, an answer, a server error message or a credential. Spend is always computed from the ledger, never from
in-memory results. Appends are multi-process safe (``memaudit.lock.locked_append``).
"""
from __future__ import annotations

import datetime as dt
import json
import math
import os
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

from ..lock import locked_append

LEDGER_SCHEMA = "memaudit-ledger/1"

ROW_FIELDS = (
    "schema", "ts", "run_id", "client", "provider", "model_requested", "model_reported", "request_hash", "prompt_sha256",
    "tag", "attempt", "attempt_id", "status", "ok", "error_code", "cached", "billing_unknown", "max_tokens", "temperature", "draw_id",
    "finish_reason", "input_tokens", "output_tokens", "reasoning_tokens", "cached_tokens", "network_ms", "queue_ms",
)
STATUSES = ("ok", "cache_hit", "http_error", "rate_limited", "timeout", "connect_error", "network_error",
            "invalid_response", "empty_output", "json_error", "blocked", "refused_cap")
# Keys that must never appear in a row (content or secrets). Checked on every append.
FORBIDDEN_KEYS = frozenset({"prompt", "system", "text", "answer", "response", "output", "error", "error_text", "message",
                            "headers", "authorization", "api_key", "key", "secret", "token"})


class LedgerError(ValueError):
    pass


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _json_safe(obj: Any) -> Any:
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    if isinstance(obj, Mapping):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    return obj


def validate_row(row: Mapping[str, Any]) -> None:
    if not isinstance(row, Mapping):
        raise LedgerError("ledger row must be a mapping")
    bad = set(row) & FORBIDDEN_KEYS
    if bad:
        raise LedgerError("forbidden content or secrets in ledger row")
    unknown = set(row) - set(ROW_FIELDS)
    if unknown:
        raise LedgerError("unknown ledger fields")
    if row.get("schema") != LEDGER_SCHEMA:
        raise LedgerError(f"row schema must be {LEDGER_SCHEMA!r}")
    if row.get("status") not in STATUSES:
        raise LedgerError("invalid ledger status")
    timestamp = row.get("ts")
    try:
        if not isinstance(timestamp, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})", timestamp):
            raise ValueError
        if dt.datetime.fromisoformat(timestamp).utcoffset() is None:
            raise ValueError
    except ValueError:
        raise LedgerError("timestamp must be a valid timezone-aware ISO datetime") from None
    for key in ("temperature", "network_ms", "queue_ms"):
        value = row.get(key)
        if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0):
            raise LedgerError("invalid finite nonnegative numeric metadata")
    for key in ("ok", "cached", "billing_unknown"):
        if row.get(key) is not None and type(row[key]) is not bool:
            raise LedgerError("invalid boolean metadata")
    if row.get("status") == "cache_hit" and row.get("cached") is not True:
        raise LedgerError("cache-hit rows require an explicit true cache flag")
    if row.get("cached") is True and row.get("status") != "cache_hit":
        raise LedgerError("cached results require cache-hit status")
    identifiers = ("run_id", "client", "provider", "model_requested", "model_reported", "tag", "draw_id", "error_code", "finish_reason", "attempt_id")
    for key in identifiers:
        value = row.get(key)
        if value is not None and (not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_.:/+-]{0,160}", value)):
            raise LedgerError("metadata must use short identifiers, never arbitrary text")
    for key in ("input_tokens", "output_tokens", "cached_tokens", "reasoning_tokens", "max_tokens", "attempt"):
        value = row.get(key)
        if value is not None and (type(value) is not int or value < 0):
            raise LedgerError("invalid nonnegative integer counter")
    if row.get("cached_tokens") is not None and row.get("input_tokens") is not None and row["cached_tokens"] > row["input_tokens"]:
        raise LedgerError("cached tokens exceed input tokens")
    for key in ("request_hash", "prompt_sha256"):
        if row.get(key) is not None and (not isinstance(row[key], str) or not re.fullmatch(r"[0-9a-f]{64}", row[key])):
            raise LedgerError("invalid request digest")


def make_row(**fields: Any) -> dict:
    """A complete row: missing fields are None, ``schema`` and ``ts`` are filled in."""
    row = {k: None for k in ROW_FIELDS}
    row.update({"schema": LEDGER_SCHEMA, "ts": utc_now_iso()})
    row.update(fields)
    validate_row(row)
    return row


class JsonlLedger:
    def __init__(self, path: str | os.PathLike):
        self.path = Path(path)

    def append(self, row: Mapping[str, Any]) -> None:
        validate_row(row)
        line = json.dumps(_json_safe(row), ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n"
        locked_append(self.path, line.encode("utf-8"))

    def read(self) -> list[dict]:
        """All rows; a corrupt line raises (a ledger with holes must not be summed silently)."""
        if not self.path.exists():
            return []
        rows = []
        with self.path.open(encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, start=1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                    validate_row(row)
                    rows.append(row)
                except json.JSONDecodeError as exc:
                    raise LedgerError(f"corrupt ledger line {lineno} in {self.path}") from exc
        return rows

    def rows_for(self, *, run_id: str | None = None, tag_prefix: str | None = None) -> list[dict]:
        out = self.read()
        if run_id is not None:
            out = [r for r in out if r.get("run_id") == run_id]
        if tag_prefix is not None:
            out = [r for r in out if str(r.get("tag") or "").startswith(tag_prefix)]
        return out


def live_attempts(rows: Iterable[Mapping[str, Any]]) -> int:
    """Attempts that reached (or may have reached) a backend: everything except cache hits and cap refusals."""
    return sum(1 for r in rows if r.get("status") not in ("cache_hit", "refused_cap"))
