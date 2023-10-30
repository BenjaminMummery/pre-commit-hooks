# Copyright (c) 2023 Benjamin Mummery

import pytest

from src._shared import exceptions
from tests.conftest import assert_matching


class TestInits:
    @staticmethod
    def test_NoCommitsError_init():
        with pytest.raises(exceptions.NoCommitsError) as e:
            raise exceptions.NoCommitsError("<sentinel>")

        assert_matching(
            "captured exception",
            "expected exception",
            e.exconly(),
            "src._shared.exceptions.NoCommitsError: <sentinel>",
        )
