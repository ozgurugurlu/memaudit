"""Usage: python examples/replica_rehearsal.py OUTPUT_DIRECTORY"""
import argparse
from pathlib import Path

from memaudit.fake import rehearse
from memaudit.provenance import write_json

parser = argparse.ArgumentParser()
parser.add_argument("output_directory", type=Path)
args = parser.parse_args()
report = rehearse(ledger=args.output_directory/"synthetic-ledger.jsonl")
write_json(args.output_directory/"synthetic-report.json", report)
print({"synthetic": report["synthetic"], "attempts": report["attempts"], "questions": report["oracle"]["n_questions"]})
