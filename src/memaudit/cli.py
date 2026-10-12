"""Only implemented offline commands are exposed by this CLI."""
# added the `qi run` command and the
# fixed optional-dependency message (no input text or paths in any error).
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import __version__
from .dense import OptionalDependencyError
from .provenance import pinned_json, json_safe, write_json


def _input(parser):
    parser.add_argument("--path", required=True, type=Path)
    parser.add_argument("--sha256", required=True)


def _output(parser): parser.add_argument("--output", type=Path)


def parser():
    p = argparse.ArgumentParser(prog="memaudit", description="Offline CPU memory benchmark measurement")
    p.add_argument("--version", action="version", version=__version__)
    commands = p.add_subparsers(dest="command", required=True)
    audit = commands.add_parser("audit").add_subparsers(dest="action", required=True)
    from .data import BENCHMARKS
    for action in ("run", "marker"):
        a = audit.add_parser(action); _input(a); _output(a)
        a.add_argument("--benchmark", required=True, choices=BENCHMARKS)
        a.add_argument("--hosts-path", type=Path); a.add_argument("--hosts-sha256")
        if action == "run":
            a.add_argument("--levels", nargs="+", choices=("raw", "F1", "F2"), default=["raw", "F1", "F2"])
            a.add_argument("--variants", nargs="+", default=None)
            a.add_argument("--folds", type=int, default=5); a.add_argument("--seed", type=int, default=0)
            a.add_argument("--n-boot", type=int, default=2000); a.add_argument("--save", type=Path)
        else:
            a.add_argument("--marker", default="\u2019"); a.add_argument("--user-only", action="store_true")
    a = audit.add_parser("report"); _input(a); _output(a); a.add_argument("--n-boot", type=int, default=2000)
    baselines = commands.add_parser("baselines").add_subparsers(dest="action", required=True)
    n = baselines.add_parser("nulls"); _output(n)
    n.add_argument("--lethe-root", required=True, type=Path); n.add_argument("--pins", required=True, type=Path); n.add_argument("--pins-sha256", required=True)
    n.add_argument("--labels", type=Path, nargs="+"); n.add_argument("--labels-sha256", nargs="+")
    replica = commands.add_parser("replica").add_subparsers(dest="action", required=True)
    r = replica.add_parser("replay"); _input(r); _output(r); r.add_argument("--n-boot", type=int, default=2000); r.add_argument("--seed", type=int, default=0)
    r.add_argument("--facts-path", type=Path); r.add_argument("--facts-sha256")
    r = replica.add_parser("rehearse"); _output(r); r.add_argument("--ledger", type=Path, required=True)
    qi = commands.add_parser("qi").add_subparsers(dest="action", required=True)
    q = qi.add_parser("run", description="Wrong-question retrieval against uniform, turn-weighted and matched-placebo nulls")
    _output(q)
    from .qi import QI_BENCHMARKS, K_PRIMARY, N_BOOT, N_WRONG
    q.add_argument("--benchmark", choices=sorted(QI_BENCHMARKS)); q.add_argument("--path", type=Path); q.add_argument("--sha256")
    q.add_argument("--hosts-path", type=Path); q.add_argument("--hosts-sha256")
    q.add_argument("--items", type=Path, help="item file in the documented contract (JSONL or JSONL.gz)"); q.add_argument("--items-sha256")
    q.add_argument("--retriever", choices=("bm25", "hybrid"), default="bm25")
    q.add_argument("--model-path", type=Path, help="local bge-small-en-v1.5 ONNX directory (hybrid only; never downloaded)")
    q.add_argument("--k", type=int, default=K_PRIMARY); q.add_argument("--n-wrong", type=int, default=N_WRONG)
    q.add_argument("--n-boot", type=int, default=N_BOOT)
    q.add_argument("--per-group-cap", type=int); q.add_argument("--total-cap", type=int)
    q.add_argument("--stratify-split", action="store_true", help="equal-weight strata by the item split field")
    return p


def _qi(a):
    from . import qi
    if a.items is not None:
        if a.benchmark or a.path or a.items_sha256 is None: raise ValueError("use either --items with --items-sha256 or --benchmark")
        dataset = qi.read_item_file(a.items, a.items_sha256)
    else:
        if a.benchmark is None or a.path is None or a.sha256 is None: raise ValueError("benchmark input and pin required")
        dataset = qi.QI_BENCHMARKS[a.benchmark](a.path, a.sha256, hosts_path=a.hosts_path, hosts_sha256=a.hosts_sha256)
    encoder = description = None
    if a.retriever == "hybrid":
        from .dense import FastEmbedEncoder
        if a.model_path is None: raise ValueError("hybrid needs --model-path")
        encoder = FastEmbedEncoder(a.model_path)
        description = encoder.describe()
    return qi.run_qi(dataset, retriever=a.retriever, encoder=encoder, encoder_description=description, k=a.k, n_wrong=a.n_wrong,
                     n_boot=a.n_boot, per_group_cap=a.per_group_cap, total_cap=a.total_cap, stratify_split=a.stratify_split)


def main(argv=None):
    p = parser(); a = p.parse_args(argv)
    try:
        if a.command == "audit":
            from . import audit, data
            if a.action == "report": result = audit.replay(a.path, a.sha256, n_boot=a.n_boot)
            else:
                kwargs = {}
                if a.benchmark == "locomo_plus":
                    if a.hosts_path is None or a.hosts_sha256 is None: raise ValueError("LoCoMo-Plus needs pinned host data")
                    kwargs = {"hosts_path": a.hosts_path, "hosts_sha256": a.hosts_sha256}
                dataset = data.load_benchmark(a.benchmark, a.path, a.sha256, **kwargs)
                if a.action == "marker": result = audit.marker_report(dataset, a.marker, user_only=a.user_only)
                else: result = audit.run_audit(dataset, levels=a.levels, variants=a.variants, folds=a.folds, seed=a.seed, n_boot=a.n_boot, save=a.save)
        elif a.command == "baselines":
            from .nulls import evaluate_lethe
            labels = None
            if a.labels or a.labels_sha256:
                if not a.labels or not a.labels_sha256 or len(a.labels) != len(a.labels_sha256) or len(a.labels) < 2:
                    raise ValueError("at least two label files and matching hash pins required")
                labels = [pinned_json(path, pin) for path, pin in zip(a.labels, a.labels_sha256)]
            result = evaluate_lethe(a.lethe_root, pinned_json(a.pins, a.pins_sha256), label_sets=labels)
        elif a.command == "qi":
            result = _qi(a)
        elif a.action == "replay":
            from .replica import replay
            result = replay(a.path, a.sha256, n_boot=a.n_boot, seed=a.seed, facts_path=a.facts_path, facts_sha256=a.facts_sha256)
        else:
            from .fake import rehearse
            result = rehearse(ledger=a.ledger)
    except OptionalDependencyError as exc:
        p.exit(2, f"memaudit: {exc}\n")
    except Exception:
        # Never include input text, paths, raw source errors, or invalid values in errors.
        p.exit(2, "memaudit: invalid input or offline execution failure; inspect the documented schema and pins\n")
    if a.output: write_json(a.output, result)
    else: print(json.dumps(json_safe(result), sort_keys=True, indent=2, allow_nan=False))
    return 0
