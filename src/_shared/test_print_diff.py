# Copyright (c) 2025-2026 Benjamin Mummery
from conftest import assert_matching

from . import print_diff


def test_print_diff():
    assert_matching(
        "output",
        "expected output",
        print_diff.format_diff("ABC", "AxxB"),
        f"  - AB{print_diff.REMOVED_COLOUR}C{print_diff.END_COLOUR}\n  + A{print_diff.ADDED_COLOUR}x{print_diff.END_COLOUR}{print_diff.ADDED_COLOUR}x{print_diff.END_COLOUR}B",
    )


def test_print_diff_with_line_no():
    assert_matching(
        "output",
        "expected output",
        print_diff.format_diff("Armour", "armor", 7),
        f"  line 7:\n  - {print_diff.REMOVED_COLOUR}A{print_diff.END_COLOUR}rmo{print_diff.REMOVED_COLOUR}u{print_diff.END_COLOUR}r\n  + {print_diff.ADDED_COLOUR}a{print_diff.END_COLOUR}rmor",
    )
