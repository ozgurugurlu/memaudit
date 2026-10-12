"""Explicit point-estimate rules; historical frozen constants remain historical."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math


@dataclass(frozen=True)
class Thresholds:
    ref_gap_pts: float = 8.9
    kill_sd_pts: float = .7
    kill_jaccard: float = .9
    kill_self_frac: float = .2
    kill_placebo_pts: float = 2.
    kill_placebo_frac: float = .1
    claim_sd_pts: float = 2.
    claim_jaccard: float = .6
    claim_self_frac: float = .5
    claim_placebo_frac: float = .5
    n_placebo: int = 20

    def __post_init__(self):
        if any(type(x) not in (int, float) or not math.isfinite(x) or x < 0 for x in asdict(self).values()) or self.ref_gap_pts == 0:
            raise ValueError("invalid registered thresholds")
        if type(self.n_placebo) is not int or self.n_placebo < 1:
            raise ValueError("positive placebo arm count required")
        if any(getattr(self, k) > 1 for k in ("kill_jaccard", "kill_self_frac", "kill_placebo_frac", "claim_jaccard", "claim_self_frac", "claim_placebo_frac")):
            raise ValueError("fraction thresholds must be in [0,1]")


def validate_card(card: dict, domains: dict[str, float | None]) -> dict:
    """Validate a numeric rule card; None and NaN explicitly mean unknown.

    Domain values are inclusive upper bounds; None means no finite upper
    bound. All known card values must be nonnegative numbers (not booleans).
    Values within 1e-12 of a finite domain boundary are clipped for roundoff.
    """
    if not isinstance(card, dict) or set(card)-set(domains):
        raise ValueError("unsupported rule card fields")
    clean = {}
    for name, value in card.items():
        if value is None:
            clean[name] = None
        elif type(value) not in (int, float):
            raise ValueError("rule inputs must be numbers or unknown")
        elif math.isnan(value):
            clean[name] = None
        elif not math.isfinite(value) or value < -1e-12 or (domains[name] is not None and value > domains[name]+1e-12):
            raise ValueError("rule input is outside its domain")
        else:
            clean[name] = max(0., value) if domains[name] is None else min(domains[name], max(0., value))
    return clean


def evaluate(card: dict, thresholds: Thresholds) -> dict:
    """Pass thresholds explicitly. `Thresholds()` encodes the historical S11 rules.

    Historical 8.9 is a frozen decision threshold, not a matched-convention
    external denominator. Never change a frozen rule after seeing outcomes.
    """
    card = validate_card(card, {"SD_W_pts": None, "J_median": 1, "G_self_pts": 50,
                                "P_placebo_ge": 1, "P_placebo_gt": 1})
    t = thresholds
    def known(*names): return all(card.get(k) is not None and math.isfinite(card[k]) for k in names)
    result = {"thresholds": asdict(t), "inputs": card,
              "reference_note": "decision thresholds are protocol constants, not a matched-population external comparison"}
    if known("SD_W_pts", "J_median"):
        sd, j = card["SD_W_pts"], card["J_median"]
        dead = sd <= t.kill_sd_pts and j >= t.kill_jaccard
        a, b = sd >= t.claim_sd_pts, j <= t.claim_jaccard
        result["rule1"] = {"fired": dead}
        result["claim1"] = {"status": "DEAD" if dead else "SUPPORTED" if a and b else "PARTIAL" if a or b else "NOT SUPPORTED"}
    else:
        result["rule1"] = {"fired": None}; result["claim1"] = {"status": "NOT_EVALUABLE"}
    if known("G_self_pts"):
        g = card["G_self_pts"]; dead = g < t.kill_self_frac*t.ref_gap_pts-1e-9
        result["rule2"] = {"fired": dead}
        result["claim2"] = {"status": "DEAD" if dead else "SUPPORTED" if g >= t.claim_self_frac*t.ref_gap_pts else "PARTIAL"}
    else:
        result["rule2"] = {"fired": None}; result["claim2"] = {"status": "NOT_EVALUABLE"}
    if known("P_placebo_ge", "P_placebo_gt"):
        dead = card["P_placebo_gt"] < t.kill_placebo_frac
        result["rule4"] = {"fired": dead}
        result["claim4"] = {"status": "DEAD" if dead else "SUPPORTED" if card["P_placebo_ge"] >= t.claim_placebo_frac else "PARTIAL"}
    else:
        result["rule4"] = {"fired": None}; result["claim4"] = {"status": "NOT_EVALUABLE"}
    fired = [k for k in ("rule1", "rule2", "rule4") if result[k]["fired"]]
    unknown = [k for k in ("rule1", "rule2", "rule4") if result[k]["fired"] is None]
    result.update(fired=fired, gate="STOP_KILL_RULE" if fired else "NOT_EVALUABLE" if unknown else "PASS")
    return result
