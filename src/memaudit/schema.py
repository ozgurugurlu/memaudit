"""Question-free units, explicit ranking pools and independent CV groups."""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Unit:
    uid: str
    turns: tuple[tuple[str, str], ...]
    user_role: str = "user"
    rel_pos: float = 0.0
    n_units: int = 1

    @classmethod
    def from_dict(cls, data: dict) -> "Unit":
        if set(data) - {"uid", "turns", "user_role", "rel_pos", "n_units"}:
            raise ValueError("forbidden unit fields: units must be query-blind")
        return cls(**{**data, "turns": tuple(tuple(t) for t in data["turns"])})


@dataclass(frozen=True, slots=True)
class AuditRow:
    pool: str
    unit: int
    label: int
    group: str
    # Position is row-level: shared host units may occupy different pool positions.
    rel_pos: float | None = None
    n_units: int | None = None


@dataclass
class AuditSet:
    name: str
    units: list[Unit]
    rows: list[AuditRow]
    meta: dict = field(default_factory=dict)

    def validate(self) -> None:
        if not self.units or not self.rows:
            raise ValueError("audit needs units and rows")
        if len({u.uid for u in self.units}) != len(self.units):
            raise ValueError("duplicate unit IDs")
        for u in self.units:
            if type(u) is not Unit or not isinstance(u.uid, str):
                raise ValueError("use question-free Unit objects")
            if not math.isfinite(u.rel_pos) or not 0 <= u.rel_pos <= 1 or u.n_units < 1:
                raise ValueError("invalid unit position")
            if any(len(t) != 2 or not all(isinstance(x, str) for x in t) for t in u.turns):
                raise ValueError("turns must be (role, text) string pairs")
        pools, units, seen = {}, {}, set()
        for r in self.rows:
            if not isinstance(r.pool, str) or not isinstance(r.group, str):
                raise ValueError("pool and group IDs must be strings")
            if not isinstance(r.unit, int) or not 0 <= r.unit < len(self.units) or r.label not in (0, 1):
                raise ValueError("invalid row index or binary label")
            if r.rel_pos is not None and (not math.isfinite(r.rel_pos) or not 0 <= r.rel_pos <= 1):
                raise ValueError("invalid row position")
            if r.n_units is not None and r.n_units < 1:
                raise ValueError("invalid row pool size")
            if pools.setdefault(r.pool, r.group) != r.group or units.setdefault(r.unit, r.group) != r.group:
                raise ValueError("a pool and each shared unit must belong to exactly one CV group")
            if (r.pool, r.unit) in seen:
                raise ValueError("duplicate unit within a ranking pool")
            seen.add((r.pool, r.unit))


def unit_hash(unit: Unit) -> str:
    # JSON avoids ambiguous separator collisions and ignores IDs, questions and positions.
    return hashlib.sha256(json.dumps(unit.turns, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
