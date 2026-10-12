# added the `qi run --help` case.
import json
import subprocess
import sys

import pytest

from memaudit.cli import main
from memaudit.provenance import sha256_file


@pytest.mark.parametrize("args", [["--help"], ["audit", "run", "--help"], ["audit", "marker", "--help"], ["audit", "report", "--help"], ["baselines", "nulls", "--help"], ["replica", "replay", "--help"], ["replica", "rehearse", "--help"], ["qi", "run", "--help"]])
def test_only_implemented_command_help(args):
    with pytest.raises(SystemExit) as e: main(args)
    assert e.value.code == 0


def test_cli_fake_and_replay_roundtrip(tmp_path):
    output = tmp_path/"report.json"
    assert main(["replica", "rehearse", "--ledger", str(tmp_path/"ledger.jsonl"), "--output", str(output)]) == 0
    assert json.loads(output.read_text())["synthetic"]
    doc = {"schema": "memaudit-replica/1", "planned_counts": {"synthetic": 2}, "questions": [
        {"id": "one", "group": "synthetic", "main": [1, 0]}, {"id": "two", "group": "synthetic", "main": [0, 1]}]}
    source = tmp_path/"synthetic.json"; source.write_text(json.dumps(doc))
    assert main(["replica", "replay", "--path", str(source), "--sha256", sha256_file(source), "--n-boot", "20", "--output", str(output)]) == 0
    assert json.loads(output.read_text())["oracle"]["union_minus_mean_pp"] == 50


def test_cli_errors_do_not_echo_sensitive_inputs(tmp_path, capsys):
    source = tmp_path/"synthetic.json"; source.write_text("not json")
    with pytest.raises(SystemExit) as e:
        main(["replica", "replay", "--path", str(source), "--sha256", "0"*64])
    assert e.value.code == 2
    assert str(tmp_path) not in capsys.readouterr().err


@pytest.mark.parametrize("command,benchmark,document", [("replica", None, []), ("replica", None, {"schema": "memaudit-replica/1", "questions": [1]}),
    ("audit", "locomo", [{"conversation": {}, "qa": []}])])
def test_cli_structural_errors_are_sanitized_exit_two(tmp_path, capsys, command, benchmark, document):
    source = tmp_path/"malformed.json"; source.write_text(json.dumps(document))
    args = [command, "replay" if command == "replica" else "marker", "--path", str(source), "--sha256", sha256_file(source)]
    if benchmark: args += ["--benchmark", benchmark]
    with pytest.raises(SystemExit) as e: main(args)
    assert e.value.code == 2
    output = capsys.readouterr()
    assert output.out == "" and "Traceback" not in output.err and str(source) not in output.err
