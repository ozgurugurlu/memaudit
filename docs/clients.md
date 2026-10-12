# Offline clients and shared infrastructure

CPU v0.1 exposes a provider-neutral protocol and an offline `FakeClient`.
It does not supply a hosted model provider, API credential reader, automatic
retry loop, or live study runner. The infrastructure supports local rehearsal;
live-provider readiness is not claimed by the existence of these interfaces.

## Protocol and FakeClient

`complete(prompt, *, system=None, max_tokens=1024, json_schema=None, tag="",
temperature=None, cache="use", draw_id=None)` returns an `LLMResult` with text,
optional parsed JSON, usage, timings, status, and a request hash.
`complete_many(requests, concurrency=1)` takes `Request` objects; the supplied
implementations execute sequentially even when a larger concurrency is passed.

Cache modes are `use`, `bypass`, `refresh`, and `only`. They are protocol fields;
the fake has no persistent response cache. `draw_id` participates in request
identity and the default fake response, allowing distinct deterministic draws.
Fake token counts are whitespace-word counts, not a model tokenizer. Its
`json_schema` path attempts JSON parsing but does not perform full JSON Schema
validation. Custom responders receive the request and return a string.

```python
from memaudit.clients import FakeClient, CappedClient, JsonlLedger

client = CappedClient(FakeClient(), ledger=JsonlLedger("runs/example-ledger.jsonl"),
                      max_calls=2, run_id="synthetic-demo")
first = client.complete("Invented fixture", draw_id="draw-1", tag="example")
second = client.complete("Invented fixture", draw_id="draw-2", tag="example")
assert first.request_hash != second.request_hash
```

This example is synthetic. A third dispatched attempt with the same run ID
and exhausted cap is refused. Reusing that run ID intentionally reuses its
ledger accounting; the default creates a fresh UUID per wrapper.

## Ledger and caps

`JsonlLedger` appends `memaudit-ledger/1` rows under an inter-process lock.
Rows contain short identifiers, request/prompt digests, status, token counts,
and timings. They exclude prompt/answer/system bodies, arbitrary errors,
headers, and credentials. Invalid fields and corrupt rows raise instead of
silently disappearing from accounting. Timestamp fields require a valid
timezone-aware ISO datetime; timings and temperature require finite,
nonnegative numbers; status flags require booleans or an explicit unknown. Use non-content IDs in tags and
draw IDs as well as in formally named identifier fields.

`CappedClient` requires `max_calls`; attempts that may have reached the backend
count, while cache hits and cap refusals do not. Paid custom clients also
require a USD cap and caller-supplied `PriceTable`. Prices are not shipped.
Unknown model prices fail instead of being treated as zero. Noncached paid
responses require valid integer input and output usage, including explicit
zero counts. Missing, partial, or malformed usage keeps billing unknown and
blocks further budgeted attempts. Malformed cache/validity flags are recorded
as failed attempts rather than coerced to booleans. The pricing
convention counts output tokens as already including reasoning tokens and
treats cached input as a subset of total input.

The wrapper serializes its check, dispatch, and result-accounting transaction
for a shared ledger. Before dispatch it writes a durable `<ledger>.pending`
reservation with a unique attempt ID. After interruption, that record is
reconciled with the ledger so the attempt is counted once; paid unknown
billing prevents further spend-authorized calls for that run. Successful
accounting removes the pending record. Do not delete a pending record to
make a cap pass. Run IDs scope accounting; changing IDs does not enforce a
study-wide budget.

This local reservation/accounting behavior is not a substitute for a
registered study's global budget, provider usage
reconciliation, or verified provider-specific token estimates. A custom
provider implementation must satisfy the declared usage and error contracts;
CPU v0.1 performs no such live integration.

## Locks and deterministic splits

`FileLock(path, ...)` selects POSIX flock where available, then the Windows
locking backend, then an exclusive-create lockfile fallback. All lock paths
are explicit. A fallback sentinel can outlive a killed process; elapsed-time
stale breaking is optional and should not be used as proof that an owner has
stopped. The implementation of multiple backends is not a statement that all
have been tested on native platforms.

`exclusive_slot(name, lock_path, ...)` offers a caller-selected heavy-job slot.
It does not automatically coordinate unrelated study harnesses. Sharing a
machine requires agreement on the same lock path and job ownership.

`memaudit.splits` supplies two distinct reproducible rules:

- Uniform split: first eight bytes, big-endian, of SHA-256 of `salt + ":" + key`,
  divided by 2^64; dev iff the result is below the chosen dev fraction.
- Rank split: sort distinct keys by SHA-256 of `prefix + key`; the first
  `n_dev` are dev, next `n_test` are test, and the remainder reserve.

Use the episode-level key when questions share a conversation, host, scenario,
or persona. A new salt defines a new assignment; it does not repair a
previously consumed test set. Hash-based group folds are available separately,
but the audit uses scikit-learn `GroupKFold`, not the hash-fold utility.
