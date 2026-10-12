import json

import pytest

from memaudit.clients import (CallCapExceeded, CappedClient, FakeClient, JsonlLedger, LedgerError, LLMClient, PriceMissing,
                              PriceTable, Request, SpendCapExceeded, make_row, request_hash)


class PaidFake(FakeClient):
    name = "paid-fake"
    provider = "paid-fake"
    paid = True


def test_fake_client_is_deterministic_and_satisfies_protocol():
    c = FakeClient()
    assert isinstance(c, LLMClient)
    a = c.complete("question one", tag="t")
    b = c.complete("question one", tag="t")
    assert a.text == b.text and a.ok and a.request_hash == b.request_hash
    d = c.complete("question one", draw_id="draw-2")
    assert d.text != a.text and d.request_hash != a.request_hash
    j = c.complete("q", json_schema={"type": "object"})
    assert isinstance(j.parsed, dict)
    many = c.complete_many([Request("x"), Request("y")])
    assert [m.text for m in many] == [c.complete("x").text, c.complete("y").text]


def test_fake_client_scripted_responder_and_failures():
    c = FakeClient(lambda req: "yes" if "capital" in req.prompt else "no", fail_every=3)
    assert c.complete("the capital").text == "yes"
    assert c.complete("other").text == "no"
    r = c.complete("third")
    assert not r.ok and r.error_code == "fake_failure"
    t = FakeClient(lambda req: "w " * 50).complete("p", max_tokens=5)
    assert t.finish_reason == "length" and t.usage["output_tokens"] == 5


def test_request_hash_covers_all_fields():
    base = Request("p")
    hashes = {request_hash("x", "m", r) for r in (base, Request("p", system="s"), Request("p", max_tokens=9), Request("p", temperature=0.7),
                                                  Request("p", draw_id="d"), Request("p", json_schema={"a": 1}))}
    assert len(hashes) == 6
    assert request_hash("x", "m", Request("p", tag="other")) == request_hash("x", "m", base)


def test_capped_client_enforces_max_calls_and_ledgers_no_content(tmp_path):
    led = JsonlLedger(tmp_path / "ledger.jsonl")
    c = CappedClient(FakeClient(), ledger=led, max_calls=3, run_id="r1")
    secret_prompt = "UNIQUE-PROMPT-MARKER about something"
    for _ in range(3):
        c.complete(secret_prompt, tag="study/arm")
    with pytest.raises(CallCapExceeded):
        c.complete(secret_prompt)
    rows = led.read()
    assert [r["status"] for r in rows] == ["ok", "ok", "ok", "refused_cap"]
    assert c.calls_used() == 3
    raw = (tmp_path / "ledger.jsonl").read_text()
    assert "UNIQUE-PROMPT-MARKER" not in raw and "fake-answer" not in raw
    assert all(r["schema"] == "memaudit-ledger/1" and len(r["prompt_sha256"]) == 64 for r in rows)
    other = CappedClient(FakeClient(), ledger=led, max_calls=1, run_id="r2")
    other.complete("x")                                          # caps are per run_id


def test_paid_client_requires_cap_and_price(tmp_path):
    led = JsonlLedger(tmp_path / "l.jsonl")
    with pytest.raises(ValueError, match="paid"):
        CappedClient(PaidFake(), ledger=led, max_calls=10)
    with pytest.raises(PriceMissing):
        CappedClient(PaidFake(), ledger=led, max_calls=10, cap_usd=1.0, prices=PriceTable.from_mapping({"other": {"input_per_mtok": 1, "output_per_mtok": 1}}))
    with pytest.raises(ValueError):
        CappedClient(FakeClient(), ledger=led, max_calls=-1)


def test_spend_cap_uses_ledger_and_worst_case(tmp_path):
    led = JsonlLedger(tmp_path / "l.jsonl")
    prices = PriceTable.from_mapping({"fake-model-v1": {"input_per_mtok": 1_000_000.0, "output_per_mtok": 0.0}})   # 1 USD per input token
    c = CappedClient(PaidFake(lambda r: "ok"), ledger=led, max_calls=100, cap_usd=10.0, prices=prices, run_id="s")
    c.complete("a b c", max_tokens=1)                           # worst case 5 bytes -> 5 USD <= 10; billed 3 tokens -> 3 USD
    assert c.spend_usd() == pytest.approx(3.0)
    with pytest.raises(SpendCapExceeded):
        c.complete("d e f g h", max_tokens=1)                   # 3 + 9 > 10: refused before sending
    assert led.read()[-1]["status"] == "refused_cap"
    assert c.spend_usd() == pytest.approx(3.0)


def test_ledger_rejects_content_and_unknown_fields_and_corruption(tmp_path):
    led = JsonlLedger(tmp_path / "l.jsonl")
    with pytest.raises(LedgerError, match="forbidden"):
        led.append({**make_row(status="ok"), "prompt": "text"})
    with pytest.raises(LedgerError, match="unknown"):
        led.append({**make_row(status="ok"), "foo": 1})
    with pytest.raises(LedgerError, match="status"):
        make_row(status="weird")
    led.append(make_row(status="ok", run_id="a", tag="x/y"))
    with open(tmp_path / "l.jsonl", "a", encoding="utf-8") as fh:
        fh.write("{not json\n")
    with pytest.raises(LedgerError, match="corrupt"):
        led.read()


def test_price_table_validation():
    with pytest.raises(ValueError):
        PriceTable.from_mapping({"m": {"input_per_mtok": -1, "output_per_mtok": 1}})
    t = PriceTable.from_mapping({"m": {"input_per_mtok": 2.0, "output_per_mtok": 4.0, "cached_input_per_mtok": 1.0}})
    row = {"status": "ok", "model_requested": "m", "input_tokens": 1_000_000, "cached_tokens": 500_000, "output_tokens": 250_000}
    assert t.row_usd(row) == pytest.approx(0.5 * 2 + 0.5 * 1 + 0.25 * 4)
    assert t.row_usd({**row, "status": "cache_hit"}) == 0.0
    json.dumps(row)
