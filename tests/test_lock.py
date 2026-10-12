import json
import multiprocessing as mp
import os
import time

import pytest

from memaudit.lock import BACKENDS, FileLock, LockTimeout, default_backend, exclusive_slot, holder, locked_append

AVAILABLE = [b for b in BACKENDS if b == "lockfile" or b == default_backend()]


def _appender(path: str, n: int, wid: int, backend: str) -> None:
    for i in range(n):
        locked_append(path, (json.dumps({"w": wid, "i": i, "pad": "x" * 300}) + "\n").encode(), backend=backend)


def _hold(lock_path: str, backend: str, seconds: float, ready) -> None:
    with FileLock(lock_path, backend=backend):
        ready.set()
        time.sleep(seconds)


@pytest.mark.parametrize("backend", AVAILABLE)
def test_lock_is_exclusive_within_and_across_objects(tmp_path, backend):
    p = tmp_path / "x.lock"
    a = FileLock(p, backend=backend, timeout_s=0)
    b = FileLock(p, backend=backend, timeout_s=0.2, poll_s=0.01)
    a.acquire()
    assert a.held
    with pytest.raises(LockTimeout):
        b.acquire()
    a.release()
    b.acquire()
    b.release()
    with pytest.raises(RuntimeError):
        with FileLock(p, backend=backend) as c:
            c.acquire()


@pytest.mark.parametrize("backend", AVAILABLE)
def test_lock_blocks_another_process(tmp_path, backend):
    ctx = mp.get_context("spawn")
    ready = ctx.Event()
    p = str(tmp_path / "y.lock")
    proc = ctx.Process(target=_hold, args=(p, backend, 1.5, ready))
    proc.start()
    assert ready.wait(30)
    with pytest.raises(LockTimeout):
        FileLock(p, backend=backend, timeout_s=0.3, poll_s=0.01).acquire()
    proc.join(30)
    with FileLock(p, backend=backend, timeout_s=5):
        pass


@pytest.mark.parametrize("backend", AVAILABLE)
def test_concurrent_appends_never_interleave(tmp_path, backend):
    ctx = mp.get_context("spawn")
    path = str(tmp_path / "ledger.jsonl")
    procs = [ctx.Process(target=_appender, args=(path, 60, w, backend)) for w in range(4)]
    for pr in procs:
        pr.start()
    for pr in procs:
        pr.join(60)
        assert pr.exitcode == 0
    lines = open(path, encoding="utf-8").read().splitlines()
    assert len(lines) == 240
    rows = [json.loads(line) for line in lines]
    assert sorted((r["w"], r["i"]) for r in rows) == [(w, i) for w in range(4) for i in range(60)]


def test_lockfile_backend_breaks_stale_lock(tmp_path):
    p = tmp_path / "z.lock"
    sentinel = tmp_path / "z.lock.lck"
    sentinel.write_text("12345")
    old = time.time() - 3600
    os.utime(sentinel, (old, old))
    with pytest.raises(LockTimeout):
        FileLock(p, backend="lockfile", timeout_s=0.1, poll_s=0.01).acquire()
    with FileLock(p, backend="lockfile", timeout_s=1, poll_s=0.01, stale_after_s=60):
        assert sentinel.exists()
    assert not sentinel.exists()


def test_exclusive_slot_records_and_clears_holder(tmp_path):
    p = tmp_path / "heavy.lock"
    with exclusive_slot("job-a", p, timeout_s=1):
        h = holder(p)
        assert h["name"] == "job-a" and h["pid"] == os.getpid()
        with pytest.raises(LockTimeout, match="job-a"):
            with exclusive_slot("job-b", p, timeout_s=0.1, poll_s=0.01):
                pass
    assert holder(p) is None


def test_unknown_backend_rejected(tmp_path):
    with pytest.raises(ValueError):
        FileLock(tmp_path / "l", backend="nfs-magic")
