# Licence status and attribution

memaudit code and documentation are licensed under [Apache-2.0](../LICENSE),
with copyright held by Özgür Uğurlu. [NOTICE](../NOTICE) carries attribution;
[PROVENANCE](../PROVENANCE.md) describes where each component comes from.

The public release contains code, synthetic examples, documentation, and aggregate
statistics. It grants no rights to benchmark data, model weights, or third-party
source files. The complete per-benchmark statement, including PersonaHub upstream
of PersonaMem-v2 and ShareGPT/UltraChat filler inside LongMemEval-S, is in
[LICENSING.md](../LICENSING.md#data-statistics-and-code-only).
Input hashes identify files; they do not authorise redistribution.

The package does not vendor benchmark prompts, Lethe's generator/scorer, or model
checkpoints. Lethe's three executable files come from a caller-supplied pinned
checkout. The optional hybrid encoder uses model files supplied locally by the
user, under their own terms. No model is downloaded by memaudit.

Dependencies retain their own licences. [The third-party inventory](third-party-inventory.md)
records observed versions, licence metadata, and the exact distribution evidence
resolving `py-rust-stemmers` 0.1.8 as MIT despite absent metadata fields.
