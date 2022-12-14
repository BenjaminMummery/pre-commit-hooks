import os
import subprocess
from contextlib import contextmanager

import pytest


@contextmanager
def cwd(path):
    oldcwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldcwd)


class TestCLI:
    @staticmethod
    def test_passes_for_no_changes(tmp_path):
        with cwd(tmp_path):
            subprocess.run(["strict-tdd"], check=True)

    @staticmethod
    def test_fails_for_mix_of_text_and_metatext(tmp_path):
        with cwd(tmp_path):
            process = subprocess.run(["strict-tdd", "docs/foo.bar", "src/foo.bar"])
        assert process.returncode == 1
