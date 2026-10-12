"""Recompute two reported aggregate identities; no outcomes or benchmark text.

Numeric source: reported aggregate inputs documented in docs/REPRODUCTION.md.
This is arithmetic on reported inputs, not a new scoring or system run.
"""
from decimal import Decimal
import json

abstain_count, released_questions = 446, 1986
category_gain_pp = Decimal("4.940584")
gain_column_total_pp = Decimal("7.668630")
rounded_overall_difference_pp = Decimal("7.7")
report = {
    "abstention_count": abstain_count,
    "released_questions": released_questions,
    "count_fraction_percent": float(100*Decimal(abstain_count)/Decimal(released_questions)),
    "category_gain_pp": float(category_gain_pp),
    "gain_column_total_pp": float(gain_column_total_pp),
    "consistent_gain_share_percent": float(100*category_gain_pp/gain_column_total_pp),
    "rounded_difference_share_percent": float(100*category_gain_pp/rounded_overall_difference_pp),
    "limits": "count/scorer property; overall abstention score assumes zero on other questions; gain share is descriptive, not causal",
}
assert round(report["count_fraction_percent"], 4) == 22.4572
assert round(report["consistent_gain_share_percent"], 4) == 64.4259
assert round(report["rounded_difference_share_percent"], 4) == 64.1634
print(json.dumps(report, sort_keys=True))
