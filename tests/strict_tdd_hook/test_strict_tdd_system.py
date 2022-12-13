import os
import subprocess
import sys
from contextlib import contextmanager


@contextmanager
def cwd(path):
    oldcwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldcwd)


def test_passes_for_no_changes(monkeypatch):
    monkeypatch.setattr(sys, "argv", [])
    subprocess.check_output(["strict-tdd"])
