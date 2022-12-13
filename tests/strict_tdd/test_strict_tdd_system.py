import sys

from strict_tdd import strict_tdd


def test_accepts_changes_if_no_src_or_test_files_changes(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["filenames", []])

    strict_tdd.main()
