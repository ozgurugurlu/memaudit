# Local, offline targets. `make ci` runs the same steps as .github/workflows/ci.yml without network access.
# Run from a disposable copy; outputs go outside the repository unless OUT is set.
PYTHON ?= $(or $(MEMAUDIT_PYTHON),python3)
OUT ?= $(or $(MEMAUDIT_CI_OUT),$(or $(TMPDIR),/tmp)/memaudit-ci)

.PHONY: test hygiene build ci examples clean

test:
	PYTHONPATH=$(CURDIR)/src OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 HF_HUB_OFFLINE=1 $(PYTHON) -m pytest -o addopts= -q -p no:cacheprovider

hygiene:
	$(PYTHON) scripts/hygiene_scan.py --root .

build:
	$(PYTHON) -m build --no-isolation --sdist --wheel --outdir $(OUT)/dist .

examples:
	mkdir -p $(OUT)/examples && cd $(OUT)/examples && export PYTHONPATH=$(CURDIR)/src && for ex in synthetic_audit synthetic_nulls synthetic_qi aggregate_arithmetic; do \
	  $(PYTHON) $(CURDIR)/examples/$$ex.py || exit 1; done && mkdir -p $(OUT)/examples/replica && $(PYTHON) $(CURDIR)/examples/replica_rehearsal.py $(OUT)/examples/replica

ci:
	MEMAUDIT_PYTHON=$(PYTHON) MEMAUDIT_CI_OUT=$(OUT) sh scripts/ci_local.sh

clean:
	rm -rf build src/memaudit.egg-info $(OUT)
