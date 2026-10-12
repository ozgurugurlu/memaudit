"""Small synthetic audit; no benchmark inputs or downloads."""
from memaudit import AuditSet, AuditRow, Unit
from memaudit.audit import run_audit

units, rows = [], []
for group in range(6):
    for index in range(40):
        evidence = index % 2
        text = f"Synthetic item {group} {index // 2} can" + ("’" if evidence else "'") + "t wait."
        units.append(Unit(f"u{group}-{index}", (("user", text),)))
        rows.append(AuditRow(f"pool{group}", len(units)-1, evidence, f"group{group}"))
report = run_audit(AuditSet("synthetic", units, rows), variants=("all",), n_boot=100)
print({"raw_auroc": report["variants"]["raw__all"]["full_population"]["auroc_macro"]["mean"],
       "F1": report["fixes"]["full_population"]["F1"]})
