"""Required content pins and text-free provenance."""
from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any


def sha256_file(path: str | Path) -> str:
    path = Path(path)
    if path.name == ".env" or path.name.startswith(".env."):
        raise ValueError("environment files are not data inputs")
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def file_info(path: str | Path, expected_sha256: str) -> dict:
    if not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected_sha256):
        raise ValueError("a full SHA-256 pin is required")
    path = Path(path)
    actual = sha256_file(path)
    if actual != expected_sha256.lower():
        raise ValueError("input SHA-256 mismatch")
    return {"sha256": actual, "bytes": path.stat().st_size}


def pinned_json(path: str | Path, expected_sha256: str) -> Any:
    file_info(path, expected_sha256)
    return json.loads(Path(path).read_text(encoding="utf-8"))


def json_safe(value: Any) -> Any:
    """Strict JSON: undefined statistics become null, never NaN/Infinity."""
    if hasattr(value, "tolist"):
        return json_safe(value.tolist())
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def write_json(path: str | Path, value: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_safe(value), indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def split_of(identifier: str, *, salt: str, fraction: float = 0.3) -> str:
    """Compatibility wrapper for the documented colon-separated split rule."""
    from .splits import split_of as split
    return split(identifier, salt=salt, dev_fraction=fraction)
