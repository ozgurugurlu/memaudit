import json
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pytest

from memaudit.clients import FakeClient, CappedClient, JsonlLedger, CallCapExceeded
from memaudit.fake import rehearse
from memaudit.provenance import file_info, json_safe, sha256_file
from memaudit.stats import cluster_mean_ci, holm, mcnemar_exact


def test_pins_are_mandatory_and_no_nonfinite_json(tmp_path):
    p = tmp_path/"synthetic.txt"; p.write_text("synthetic")
    assert file_info(p, sha256_file(p))["bytes"] == 9
    for pin in ("", "0"*64, None):
        with pytest.raises(ValueError): file_info(p, pin)
    assert json_safe([float("nan"), float("inf")]) == [None, None]
    # The guard rejects this name before trying to open it.
    with pytest.raises(ValueError): sha256_file(tmp_path/".env")


def test_shared_statistical_edges():
    assert mcnemar_exact([1, 0], [1, 0])["p"] == 1
    assert mcnemar_exact([1]*10, [0]*10)["p"] == pytest.approx(2/1024)
    assert holm([.01, .04, .03]) == pytest.approx([.03, .06, .06])
    assert cluster_mean_ci([1., 0.], ["a", "a"])["lo"] is None
    assert cluster_mean_ci([1., 1.], ["a", "b"], n_boot=20)["lo"] == 1


def test_exception_counts_as_attempt_without_disclosing_error(tmp_path):
    sentinel = "s"+"k-"+"X"*32
    def raises(req): raise RuntimeError(sentinel)
    ledger = JsonlLedger(tmp_path/"fail.jsonl"); client = CappedClient(FakeClient(raises), ledger=ledger, max_calls=1)
    with pytest.raises(RuntimeError) as error: client.complete(sentinel)
    assert sentinel not in str(error.value) and sentinel not in ledger.path.read_text()
    assert client.calls_used() == 1
    with pytest.raises(CallCapExceeded): client.complete("synthetic")


def test_concurrent_capped_clients_share_atomic_cap(tmp_path):
    ledger = JsonlLedger(tmp_path/"ledger.jsonl")
    clients = [CappedClient(FakeClient(), ledger=ledger, max_calls=2, run_id="shared") for _ in range(8)]
    def call(c):
        try: c.complete("synthetic"); return 1
        except CallCapExceeded: return 0
    with ThreadPoolExecutor(max_workers=8) as pool: successes = sum(pool.map(call, clients))
    assert successes == 2 and clients[0].calls_used() == 2


def test_rehearsal_uses_real_protocol_and_content_free_ledger(tmp_path):
    ledger = tmp_path/"rehearsal.jsonl"
    result = rehearse(ledger=ledger, groups=2, questions=3, replicas=3)
    assert result["synthetic"] and result["attempts"] == 54
    assert "synthetic item" not in ledger.read_text()
    assert all(json.loads(line)["schema"] == "memaudit-ledger/1" for line in ledger.read_text().splitlines())


def test_crash_reservation_survives_and_counts_toward_restarted_cap(tmp_path):
    def interrupted(req): raise SystemExit("synthetic interruption")
    ledger = JsonlLedger(tmp_path/"crash.jsonl")
    first = CappedClient(FakeClient(interrupted), ledger=ledger, max_calls=1, run_id="restart")
    with pytest.raises(SystemExit): first.complete("synthetic")
    assert first.calls_used() == 1
    second = CappedClient(FakeClient(), ledger=ledger, max_calls=1, run_id="restart")
    with pytest.raises(CallCapExceeded): second.complete("synthetic")
    assert second.calls_used() == 1 and ledger.read()[0]["error_code"] == "interrupted_attempt"
    assert not first._pending_path.exists()


@pytest.mark.parametrize("usage", [{}, {"input_tokens": 1}, {"output_tokens": 0},
    {"input_tokens": True, "output_tokens": 0}, {"input_tokens": 1, "output_tokens": -1},
    {"input_tokens": 1, "output_tokens": 0, "cached_tokens": 2}])
def test_paid_missing_or_invalid_usage_fails_closed(tmp_path, usage):
    from memaudit.clients.base import LLMResult
    from memaudit.clients.caps import Price, PriceTable, SpendCapExceeded
    class SyntheticPaid:
        name = provider = model = "synthetic-paid"
        paid = True
        calls = 0
        def complete(self, *args, **kwargs):
            self.calls += 1
            return LLMResult("invented", usage=usage)
    inner = SyntheticPaid(); ledger = JsonlLedger(tmp_path/"usage.jsonl")
    client = CappedClient(inner, ledger=ledger, max_calls=3, cap_usd=.000004,
                          prices=PriceTable({inner.model: Price(1, 1)}))
    client.complete("abc", max_tokens=1)
    assert ledger.read()[0]["billing_unknown"] is True
    with pytest.raises(SpendCapExceeded): client.complete("abc", max_tokens=1)
    with pytest.raises(SpendCapExceeded): client.spend_usd()
    assert inner.calls == 1 and client.calls_used() == 1


def test_paid_explicit_zero_usage_and_true_cache_hits_are_known(tmp_path):
    from memaudit.clients.base import LLMResult
    from memaudit.clients.caps import Price, PriceTable
    class SyntheticPaid:
        name = provider = model = "synthetic-paid"
        paid = True
        cached = False
        def complete(self, *args, **kwargs):
            return LLMResult("invented", usage={} if self.cached else {"input_tokens": 0, "output_tokens": 0}, cached=self.cached)
    inner = SyntheticPaid(); ledger = JsonlLedger(tmp_path/"known.jsonl")
    client = CappedClient(inner, ledger=ledger, max_calls=2, cap_usd=.01, prices=PriceTable({inner.model: Price(1, 1)}))
    client.complete("abc", max_tokens=1); inner.cached = True; client.complete("abc", max_tokens=1)
    assert client.spend_usd() == 0 and client.calls_used() == 1
    assert [r["billing_unknown"] for r in ledger.read()] == [False, False]


@pytest.mark.parametrize("field,value", [("cached", "False"), ("cached", 1), ("ok", "False"), ("ok", None)])
def test_malformed_result_flags_cannot_bypass_call_or_spend_caps(tmp_path, field, value):
    from memaudit.clients.base import LLMResult
    from memaudit.clients.caps import Price, PriceTable, SpendCapExceeded
    class SyntheticPaid:
        name = provider = model = "synthetic-paid"
        paid = True
        calls = 0
        def complete(self, *args, **kwargs):
            self.calls += 1
            result = LLMResult("invented", usage={"input_tokens": 1, "output_tokens": 0})
            setattr(result, field, value)
            return result
    inner = SyntheticPaid(); ledger = JsonlLedger(tmp_path/"flags.jsonl")
    client = CappedClient(inner, ledger=ledger, max_calls=2, cap_usd=.01, prices=PriceTable({inner.model: Price(1, 1)}))
    with pytest.raises(RuntimeError): client.complete("abc", max_tokens=1)
    with pytest.raises(SpendCapExceeded): client.complete("abc", max_tokens=1)
    assert inner.calls == 1 and client.calls_used() == 1 and ledger.read()[0]["billing_unknown"] is True


def test_ledger_rejects_text_or_wrong_types_in_every_typed_metadata_field(tmp_path):
    from memaudit.clients.ledger import LedgerError, make_row
    sentinel = "synthetic arbitrary private content"
    ledger = JsonlLedger(tmp_path/"metadata.jsonl")
    invalid = [(field, value) for field in ("network_ms", "queue_ms", "temperature")
               for value in (sentinel, {"text": sentinel}, [sentinel], True, -1, float("nan"), float("inf"))]
    invalid += [(field, value) for field in ("ok", "cached", "billing_unknown") for value in (sentinel, 1, {})]
    invalid += [("ts", value) for value in (sentinel, "2026-99-03T00:00:00Z", "2026-10-03", None, 1)]
    for field, value in invalid:
        with pytest.raises(LedgerError): ledger.append(make_row(status="ok", **{field: value}))
    assert not ledger.path.exists()
    with pytest.raises(LedgerError): make_row(status="cache_hit", cached=False)
    with pytest.raises(LedgerError): make_row(status="ok", cached=True)
