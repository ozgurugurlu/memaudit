"""Four deterministic ForgetEval policies and explicit preservation scoring.

The public scorer is executed from user-supplied, hash-pinned Lethe source.
No benchmark cases, prompts, annotations or code from Lethe are distributed.
"""
from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
import math
from pathlib import Path
import re
import sys
import threading
import types
from numbers import Integral

from .provenance import file_info

LETHE_FILES = ("bench/forgeteval/generate.py", "bench/forgeteval/adversarial_generated.py", "bench/forgeteval/adversarial.py")
_IMPORT_LOCK = threading.Lock()


def phrase_hit(needle: str, text: str) -> bool:
    return bool(needle.strip()) and re.search(r"(?<!\w)"+re.escape(needle.strip().lower())+r"(?!\w)", text.lower()) is not None


def _norm(text):
    return " ".join(text.lower().split())


def fact_roles(case) -> list[str]:
    roles = []
    for fact in case.setup_facts:
        forbidden = any(phrase_hit(n, fact) for n in case.must_not_contain)
        substring = any(n.lower() in fact.lower() for n in case.must_not_contain)
        required = any(n.lower() in fact.lower() for n in case.must_contain)
        roles.append("COMPOUND" if forbidden and required else "TARGET" if forbidden else "REQUIRED" if required else "SUBSTR" if substring else "UNFLAGGED")
    return roles


def derive_keep(case, layer: str, label_sets=None) -> dict:
    roles = fact_roles(case)
    def failure(reason): return {"derivable": False, "reason": reason, "keep": []}
    if "COMPOUND" in roles: return failure("compound")
    if layer == "template":
        return {"derivable": True, "reason": "construction rule", "keep": [i for i, r in enumerate(roles) if r != "TARGET"]}
    if layer != "adversarial": raise ValueError("unknown ForgetEval layer")
    if label_sets is None or len(label_sets) < 2: return failure("missing independent labels")
    sets = [{int(k): v for k, v in labels.items()} for labels in label_sets]
    if any(set(s) != set(range(len(roles))) for s in sets): return failure("missing labels")
    keep = []
    for i, role in enumerate(roles):
        labels = [s[i] for s in sets]
        if any(l not in ("KEEP", "REMOVE") for l in labels): return failure("unsure or invalid label")
        if len(set(labels)) != 1: return failure("label disagreement")
        if (role == "TARGET" and labels[0] != "REMOVE") or (role == "REQUIRED" and labels[0] != "KEEP"):
            return failure("role conflict")
        if labels[0] == "KEEP": keep.append(i)
    return {"derivable": True, "reason": "strict role and independent-label agreement", "keep": keep}


def _bm25_order(texts, query):
    docs = [re.findall(r"\w+", t.lower()) for t in texts]; q = set(re.findall(r"\w+", query.lower()))
    n = len(docs); avg = sum(map(len, docs))/n if n else 1
    df = Counter(t for doc in docs for t in set(doc)); scores = []
    for i, doc in enumerate(docs):
        tf = Counter(doc); score = 0.
        for t in q:
            f = tf[t]
            if f:
                score += math.log1p((n-df[t]+.5)/(df[t]+.5))*f*2.5/(f+1.5*(.25+.75*len(doc)/(avg or 1)))
        scores.append((-score, i))
    return [i for _, i in sorted(scores)]


class NullPolicy:
    """Fresh per-case adapter; oracle retrieval is deterministic CPU BM25.

    store-nothing never stores replacements; wipe-plus-replacement clears on EVERY
    mutation and stores the new statement on supersede; keep-all only appends;
    oracle-target deletes whole facts matching forbidden phrases before appending.
    """
    NAMES = ("store-nothing", "wipe-plus-replacement", "keep-all", "oracle-target")

    def __init__(self, name: str, *, must_not=(), recall_ranker=None, recall_provenance=None):
        if name not in self.NAMES: raise ValueError("unknown null policy")
        if recall_ranker is not None:
            if name != "oracle-target" or not callable(recall_ranker): raise ValueError("ranker injection is for oracle-target only")
            if not isinstance(recall_provenance, dict) or set(recall_provenance) != {"method", "sha256"}:
                raise ValueError("injected ranker requires method and SHA-256 provenance")
            if not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", recall_provenance["method"]) or not re.fullmatch(r"[0-9a-f]{64}", recall_provenance["sha256"]):
                raise ValueError("invalid ranker provenance")
        elif recall_provenance is not None: raise ValueError("ranker provenance requires a ranker")
        self.recall_ranker, self.recall_provenance = recall_ranker, recall_provenance
        self.name, self.must_not = name, tuple(must_not); self.reset()

    def reset(self): self.facts = []

    def inscribe(self, text):
        if self.name == "store-nothing": return 0
        self.facts.append(text); return len(self.facts)-1

    def _mutate(self):
        before = len(self.facts)
        if self.name == "wipe-plus-replacement": self.facts = []
        elif self.name == "oracle-target": self.facts = [t for t in self.facts if not any(phrase_hit(n, t) for n in self.must_not)]
        return before - len(self.facts)

    def supersede(self, old_query, new_text):
        self._mutate(); self.inscribe(new_text)

    def release(self, query): return self._mutate()

    def purge(self, query): return self._mutate()

    def recall_texts(self, query, k=5):
        if k < 0: raise ValueError("k must be nonnegative")
        if self.recall_ranker is not None and self.facts:
            order = list(self.recall_ranker(tuple(self.facts), query))
            if any(not isinstance(i, Integral) or isinstance(i, bool) for i in order) or sorted(order) != list(range(len(self.facts))):
                raise ValueError("ranker must return a permutation of all active fact indices")
        else:
            order = _bm25_order(self.facts, query) if self.name == "oracle-target" else range(len(self.facts))
        texts = [self.facts[i] for i in order]
        return texts[:k] if k else texts


def score_case(case, policy: NullPolicy, derivation=None) -> dict:
    """Run pinned native public scoring, then query the SAME final memory state."""
    error = None
    try: public = bool(case.run(policy))
    except Exception: public, error = False, "native execution failed"
    keep = derivation["keep"] if derivation and derivation["derivable"] else None
    lost = None if keep is None else sum(not any(_norm(case.setup_facts[i]) in _norm(text) for text in policy.recall_texts(case.setup_facts[i], k=10)) for i in keep)
    return {"public": public, "derivable": keep is not None, "must_keep": len(keep) if keep is not None else None,
            "lost_required_facts": lost, "preservation": lost == 0 if lost is not None else None,
            "collateral_aware": bool(public and lost == 0) if lost is not None else None, "error": error}


@contextmanager
def pinned_lethe(repo, pins):
    """Execute only the three pinned local sources, with no bytecode writes.

    Pins authenticate bytes, not trustworthiness: use a reviewed Lethe checkout.
    Isolated module installation is temporary and refuses existing bench modules.
    """
    root = Path(repo).resolve()
    if set(pins) != set(LETHE_FILES): raise ValueError("Lethe pins must name exactly the three required source files")
    infos = {name: file_info(root/name, pins[name]) for name in LETHE_FILES}
    names = ["bench", "bench.forgeteval"] + [p[:-3].replace("/", ".") for p in LETHE_FILES]
    with _IMPORT_LOCK:
        if any(name in sys.modules for name in names): raise ValueError("bench modules already loaded; use a fresh Python process")
        try:
            for name in names[:2]:
                module = types.ModuleType(name); module.__path__ = []; sys.modules[name] = module
            for relative, name in zip(LETHE_FILES, names[2:]):
                path = (root/relative).resolve()
                if not path.is_relative_to(root): raise ValueError("Lethe source symlink escapes supplied root")
                # Compile directly: importlib loaders could write caches beside source.
                module = types.ModuleType(name); module.__package__ = name.rsplit(".", 1)[0]
                sys.modules[name] = module
                exec(compile(path.read_bytes(), "<pinned-lethe-source>", "exec"), module.__dict__)
            yield sys.modules[names[2]], sys.modules[names[4]], infos
        finally:
            for name in reversed(names): sys.modules.pop(name, None)


def evaluate_lethe(repo, pins, *, n_per_family=200, seed=42, distractors=4, label_sets=None, oracle_ranker=None, oracle_ranker_provenance=None) -> dict:
    if n_per_family < 1 or distractors < 0: raise ValueError("invalid template generation parameters")
    result = {"schema": "memaudit-nulls/1", "policies": {}, "parameters": {"n_per_family": n_per_family, "seed": seed, "distractors": distractors, "language": "en"},
              "preservation_rule": "strict construction rule for templates; at least two agreeing supplied label sets plus role consistency for adversarial",
              "oracle_retrieval": "CPU BM25 word tokens, k1=1.5 b=.75; different from original hybrid retrieval",
              "limits": "public assertion scores are not retained-memory quality; absent adversarial labels mean unknown preservation"}
    if oracle_ranker is not None:
        NullPolicy("oracle-target", recall_ranker=oracle_ranker, recall_provenance=oracle_ranker_provenance)
        result["oracle_retrieval"] = {**oracle_ranker_provenance, "provenance_status": "caller declared; no model loaded by memaudit"}
    with pinned_lethe(repo, pins) as (generate, adversarial, infos):
        result["inputs"] = infos
        cases = [("template", c) for c in generate.generate(n_per_family, seed=seed, distractors=distractors, lang="en")]
        cases += [("adversarial", c) for c in adversarial.ADVERSARIAL_TESTS]
        if len({c.id for _, c in cases}) != len(cases): raise ValueError("duplicate native case IDs")
        for layer in ("template", "adversarial"):
            result["policies"][layer] = {}
            for name in NullPolicy.NAMES:
                scores = []; reasons = Counter()
                for ly, c in cases:
                    if ly != layer: continue
                    supplied = None if label_sets is None else [s.get(c.id, {}) for s in label_sets]
                    derived = derive_keep(c, ly, supplied)
                    reasons[derived["reason"]] += 1
                    ranker_args = {"recall_ranker": oracle_ranker, "recall_provenance": oracle_ranker_provenance} if name == "oracle-target" else {}
                    scores.append(score_case(c, NullPolicy(name, must_not=c.must_not_contain, **ranker_args), derived))
                known = [s for s in scores if s["derivable"]]
                result["policies"][layer][name] = {"n_cases": len(scores), "public_pass": sum(s["public"] for s in scores),
                    "n_preservation_evaluable": len(known), "n_preservation_unknown": len(scores)-len(known),
                    "public_pass_on_evaluable": sum(s["public"] for s in known), "preservation_pass": sum(s["preservation"] for s in known),
                    "collateral_aware_pass": sum(s["collateral_aware"] for s in known), "lost_required_facts": sum(s["lost_required_facts"] for s in known),
                    "required_facts": sum(s["must_keep"] for s in known), "native_errors": sum(s["error"] is not None for s in scores), "derivation_reasons": dict(reasons)}
    return result
