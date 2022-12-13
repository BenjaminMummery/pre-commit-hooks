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
    subprocess.run("strict-tdd", check=True)


def test_passes_for_changes_to_non_src_test_files(monkeypatch):
    # GIVEN
    monkeypatch.setattr(sys, "argv", ["dummy.xt", "docs/floop.blah"])

    # WHEN
    completed_process = subprocess.run("strict-tdd")

    # THEN
    assert completed_process.returncode == 1


# def test_fails_for_changes_in_src_and_tests(monkeypatch):
#     monkeypatch.setattr(sys, "argv", [])
