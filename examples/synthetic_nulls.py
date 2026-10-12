"""Four policies on invented facts; no Lethe source or benchmark data needed."""
import json
from memaudit.nulls import NullPolicy

result = {}
for name in NullPolicy.NAMES:
    policy = NullPolicy(name, must_not=("cobalt",))
    policy.inscribe("The invented locker marker is cobalt.")
    policy.inscribe("The invented parcel code is cedar.")
    policy.supersede("locker marker", "The invented locker marker is amber.")
    recalled = policy.recall_texts("cedar", k=10)
    result[name] = {
        "remaining_facts": len(policy.facts),
        "old_marker_present": any("cobalt" in fact for fact in recalled),
        "replacement_present": any("amber" in fact for fact in recalled),
        "unrelated_fact_preserved": any("cedar" in fact for fact in recalled),
    }
assert result["store-nothing"]["remaining_facts"] == 0
assert result["wipe-plus-replacement"]["replacement_present"]
assert not result["wipe-plus-replacement"]["unrelated_fact_preserved"]
assert result["keep-all"]["old_marker_present"]
assert result["oracle-target"]["unrelated_fact_preserved"]
assert not result["oracle-target"]["old_marker_present"]
print(json.dumps({"synthetic": True, "policies": result}, sort_keys=True))
