# Copyright (c) 2023 - 2026 Benjamin Mummery

import typing

import pytest

from conftest import assert_matching
from src._shared import exceptions


@typing.no_type_check
def raiser(exception: Exception):
    raise exception("<sentinel>")


class TestInits:
    @staticmethod
    def test_NoCommitsError_init():
        with pytest.raises(exceptions.NoCommitsError) as e:
            raiser(exceptions.NoCommitsError)

        assert_matching(
            "captured exception",
            "expected exception",
            e.exconly(),
            "src._shared.exceptions.NoCommitsError: <sentinel>",
        )

    @staticmethod
    def test_InvalidConfigError_init():
        with pytest.raises(exceptions.InvalidConfigError) as e:
            raiser(exceptions.InvalidConfigError)

        assert_matching(
            "captured exception",
            "expected exception",
            e.exconly(),
            "src._shared.exceptions.InvalidConfigError: <sentinel>",
        )
