# Copyright (c) 2025 Benjamin Mummery

from conftest import assert_matching

from . import print_diff


def test_print_diff(capsys):
    # WHEN
    print_diff.print_diff("ABC", "AxxB")

    # THEN
    captured = capsys.readouterr()
    assert_matching(
        "output",
        "expected output",
        captured.out,
        f"  - AB{print_diff.REMOVED_COLOUR}C{print_diff.END_COLOUR}\n  + A{print_diff.ADDED_COLOUR}x{print_diff.END_COLOUR}{print_diff.ADDED_COLOUR}x{print_diff.END_COLOUR}B",
    )


def test_print_diff_with_line_no(capsys):
    # WHEN
    print_diff.print_diff("Armour", "armor", 7)

    # THEN
    captured = capsys.readouterr()
    assert_matching(
        "output",
        "expected output",
        captured.out,
        f"  line 7:\n  - {print_diff.REMOVED_COLOUR}A{print_diff.END_COLOUR}rmo{print_diff.REMOVED_COLOUR}u{print_diff.END_COLOUR}r\n  + {print_diff.ADDED_COLOUR}a{print_diff.END_COLOUR}rmor",
    )
