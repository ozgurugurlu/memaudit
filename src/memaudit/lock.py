"""Portable inter-process file lock (POSIX ``fcntl.flock``, Windows ``msvcrt.locking``, or an O_EXCL lock-file fallback).

Used for two things: appending ledger rows from several processes, and an optional "one heavy job at a time" slot
(``exclusive_slot``) for users who run large embedding or model jobs on a shared machine. There is no default lock
location: the caller passes a path.

    from memaudit.lock import FileLock, exclusive_slot
    with FileLock("runs/.ledger.lock", timeout_s=30):
        ...
    with exclusive_slot("embed-stale", "runs/.heavy.lock", timeout_s=7200):
        ...

Backends are chosen automatically (``fcntl`` where it exists, else ``msvcrt``, else ``lockfile``); tests can force one.
The ``lockfile`` backend works on any filesystem that honours ``O_CREAT | O_EXCL`` but is not released if the process is
killed; ``stale_after_s`` lets a waiter break such a lock.
"""
from __future__ import annotations

import contextlib
import json
import os
import time
from pathlib import Path
from typing import Iterator

try:                                   # POSIX
    import fcntl as _fcntl
except ImportError:                    # pragma: no cover - Windows
    _fcntl = None
try:                                   # Windows
    import msvcrt as _msvcrt
except ImportError:
    _msvcrt = None

BACKENDS = ("fcntl", "msvcrt", "lockfile")


class LockTimeout(TimeoutError):
    """The lock could not be acquired within ``timeout_s``."""


def default_backend() -> str:
    if _fcntl is not None:
        return "fcntl"
    if _msvcrt is not None:  # pragma: no cover - Windows
        return "msvcrt"
    return "lockfile"


class FileLock:
    """Exclusive lock on ``path`` (re-entrant use from one thread is not supported).

    ``timeout_s=None`` waits forever; ``0`` tries once. ``poll_s`` is the retry interval for the non-blocking backends.
    """

    def __init__(self, path: str | os.PathLike, *, timeout_s: float | None = None, poll_s: float = 0.05,
                 backend: str | None = None, stale_after_s: float | None = None):
        self.path = Path(path)
        self.timeout_s = timeout_s
        self.poll_s = float(poll_s)
        self.backend = backend or default_backend()
        if self.backend not in BACKENDS:
            raise ValueError(f"unknown lock backend {self.backend!r}")
        if self.backend == "fcntl" and _fcntl is None:
            raise RuntimeError("fcntl backend unavailable on this platform")
        if self.backend == "msvcrt" and _msvcrt is None:
            raise RuntimeError("msvcrt backend unavailable on this platform")
        self.stale_after_s = stale_after_s
        self._fd: int | None = None

    # ------------------------------------------------------------------ backend primitives (non-blocking try)
    def _try_acquire(self) -> bool:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.backend == "lockfile":
            sentinel = self._sentinel()
            try:
                fd = os.open(sentinel, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            except FileExistsError:
                self._maybe_break_stale(sentinel)
                return False
            os.write(fd, str(os.getpid()).encode("ascii"))
            self._fd = fd
            return True
        fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o644)
        try:
            if self.backend == "fcntl":
                _fcntl.flock(fd, _fcntl.LOCK_EX | _fcntl.LOCK_NB)
            else:  # pragma: no cover - Windows
                _msvcrt.locking(fd, _msvcrt.LK_NBLCK, 1)
        except OSError:
            os.close(fd)
            return False
        self._fd = fd
        return True

    def _sentinel(self) -> Path:
        return Path(str(self.path) + ".lck")

    def _maybe_break_stale(self, sentinel: Path) -> None:
        if self.stale_after_s is None:
            return
        with contextlib.suppress(OSError):
            if time.time() - sentinel.stat().st_mtime > self.stale_after_s:
                sentinel.unlink()

    def acquire(self) -> None:
        if self._fd is not None:
            raise RuntimeError("lock already held by this object")
        deadline = None if self.timeout_s is None else time.monotonic() + float(self.timeout_s)
        while not self._try_acquire():
            if deadline is not None and time.monotonic() >= deadline:
                raise LockTimeout(f"lock {self.path} busy for {self.timeout_s}s (backend {self.backend})")
            time.sleep(self.poll_s)

    def release(self) -> None:
        fd, self._fd = self._fd, None
        if fd is None:
            return
        try:
            if self.backend == "fcntl":
                _fcntl.flock(fd, _fcntl.LOCK_UN)
            elif self.backend == "msvcrt":  # pragma: no cover - Windows
                with contextlib.suppress(OSError):
                    os.lseek(fd, 0, os.SEEK_SET)
                    _msvcrt.locking(fd, _msvcrt.LK_UNLCK, 1)
        finally:
            os.close(fd)
            if self.backend == "lockfile":
                with contextlib.suppress(FileNotFoundError):
                    self._sentinel().unlink()

    @property
    def held(self) -> bool:
        return self._fd is not None

    def __enter__(self) -> "FileLock":
        self.acquire()
        return self

    def __exit__(self, *exc) -> None:
        self.release()


def locked_append(path: str | os.PathLike, data: bytes, *, lock_path: str | os.PathLike | None = None,
                  timeout_s: float | None = 60.0, backend: str | None = None) -> None:
    """Append ``data`` to ``path`` as one write under an exclusive lock (``lock_path`` defaults to ``path + '.lock'``)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(lock_path or Path(str(path) + ".lock"), timeout_s=timeout_s, backend=backend):
        fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
        try:
            view = memoryview(data)
            while view:
                view = view[os.write(fd, view):]
        finally:
            os.close(fd)


def holder(lock_path: str | os.PathLike) -> dict | None:
    """Best-effort view of the current ``exclusive_slot`` holder (None if nobody or unreadable)."""
    try:
        return json.loads(Path(str(lock_path) + ".info").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


@contextlib.contextmanager
def exclusive_slot(name: str, lock_path: str | os.PathLike, *, timeout_s: float = 7200.0, poll_s: float = 2.0,
                   backend: str | None = None) -> Iterator[None]:
    """At most one holder at a time across processes; the holder's name, pid and start time go to ``<lock>.info``."""
    info = Path(str(lock_path) + ".info")
    lock = FileLock(lock_path, timeout_s=timeout_s, poll_s=poll_s, backend=backend)
    try:
        lock.acquire()
    except LockTimeout as exc:
        raise LockTimeout(f"{exc} (holder: {holder(lock_path)})") from None
    try:
        info.write_text(json.dumps({"name": name, "pid": os.getpid(), "since_unix": time.time()}), encoding="utf-8")
        try:
            yield
        finally:
            with contextlib.suppress(OSError):
                info.unlink()
    finally:
        lock.release()
