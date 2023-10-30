# Copyright (c) 2023 Benjamin Mummery

import pytest

from src._shared import exceptions
from tests.conftest import assert_matching


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
