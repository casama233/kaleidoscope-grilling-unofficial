"""Reuse explicitly selected source checks within one receipt-bound invocation.

The caller owns the existing before/after source boundary. This is temporary
in-memory command reuse, not gameplay acceptance or a cross-run cache.
"""
from contextlib import contextmanager
import os
from pathlib import Path
import subprocess

SESSION_ENV = "_GRILLING_CURRENT_SOURCE_SESSION"
_successful_checks = None


@contextmanager
def current_source_validation_session():
    global _successful_checks
    if _successful_checks is not None:
        raise RuntimeError("source validation session is already active")
    _successful_checks = {}
    try:
        yield
    finally:
        _successful_checks = None


def session_active():
    return _successful_checks is not None


def run_checked_once(command, *, cwd=None, env=None):
    if not session_active():
        return subprocess.run(command, cwd=cwd, env=env, check=True)
    # No source hashes here: the outer immutable-source boundary detects drift.
    # Different arguments, working directory or effective environment rerun.
    environment = dict(os.environ if env is None else env)
    key = (tuple(map(str, command)), str(Path(cwd or Path.cwd()).resolve()),
           tuple(sorted(environment.items())))
    if key in _successful_checks:
        return _successful_checks[key]
    result = subprocess.run(command, cwd=cwd, env=environment, check=True)
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, command)
    _successful_checks[key] = result
    return result
