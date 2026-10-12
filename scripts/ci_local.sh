#!/bin/sh
# Offline local equivalent of .github/workflows/ci.yml. Run from a disposable copy of the repository.
# No network: the build uses --no-isolation (setuptools>=77 and build must already be installed) and the wheel is
# unpacked into a private directory instead of resolving dependencies; the current interpreter supplies them.
# Usage: MEMAUDIT_PYTHON=python3.12 MEMAUDIT_CI_OUT=/some/tmp/dir sh scripts/ci_local.sh
set -eu
PY="${MEMAUDIT_PYTHON:-python3}"
OUT="${MEMAUDIT_CI_OUT:-${TMPDIR:-/tmp}/memaudit-ci}"
ROOT="$(pwd)"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 HF_HUB_OFFLINE=1
rm -rf "$OUT"; mkdir -p "$OUT"
echo "== 1/6 source test suite"
PYTHONPATH="$ROOT/src" "$PY" -m pytest -o addopts= -q -p no:cacheprovider
echo "== 2/6 release-hygiene scan"
"$PY" scripts/hygiene_scan.py --root .
echo "== 3/6 sdist and wheel (offline, no build isolation)"
"$PY" -m build --no-isolation --sdist --wheel --outdir "$OUT/dist" .
echo "== 4/6 unpack the wheel and check the import location"
mkdir -p "$OUT/site"
"$PY" -m zipfile -e "$OUT"/dist/*.whl "$OUT/site"
PYTHONPATH="$OUT/site" "$PY" -c "import sys, memaudit; assert memaudit.__file__.startswith(sys.argv[1]), memaudit.__file__; print('installed', memaudit.__version__)" "$OUT/site"
echo "== 5/6 CLI and synthetic examples against the unpacked wheel"
cd "$OUT"
PYTHONPATH="$OUT/site" "$PY" -m memaudit --version
PYTHONPATH="$OUT/site" "$PY" -m memaudit replica rehearse --ledger "$OUT/ledger.jsonl" --output "$OUT/rehearsal.json"
for ex in synthetic_audit synthetic_nulls synthetic_qi aggregate_arithmetic; do
  PYTHONPATH="$OUT/site" "$PY" "$ROOT/examples/$ex.py"
done
mkdir -p "$OUT/replica-example"
PYTHONPATH="$OUT/site" "$PY" "$ROOT/examples/replica_rehearsal.py" "$OUT/replica-example"
cd "$ROOT"
echo "== 6/6 test suite against the unpacked wheel"
PYTHONPATH="$OUT/site" "$PY" -m pytest -o addopts= -q -p no:cacheprovider --import-mode=importlib
echo "local CI passed; artifacts in $OUT/dist"
