import json

import pytest

from alien_json_to_text import alien_json_to_text
from alien_text_to_json import alien_text_to_json


def test_matches_example_format():
    grid = [
        ["#000000"] * 8,
        ["#000000", "#000000", "#000000", "#0000FF", "#0000FF", "#000000", "#000000", "#000000"],
        ["#000000", "#000000", "#0000FF", "#0000FF", "#0000FF", "#0000FF", "#000000", "#000000"],
        ["#000000", "#0000FF", "#FFFFFF", "#0000FF", "#0000FF", "#FFFFFF", "#0000FF", "#000000"],
    ]
    lines = alien_json_to_text(grid)
    assert lines == [
        "3",
        "A#000000",
        "B#0000FF",
        "C#FFFFFF",
        "4",
        "8",
        "AAAAAAAA",
        "AAABBAAA",
        "AABBBBAA",
        "ABCBBCBA",
    ]


def test_round_trips_through_text_to_json():
    grid = [["#FF0000", "#00FF00"], ["#0000FF", "#FFFFFF"]]
    text_lines = alien_json_to_text(grid)
    json_lines = alien_text_to_json(text_lines)
    assert json.loads("\n".join(json_lines)) == grid


def test_each_row_uses_one_character_per_cell():
    grid = [["#111111", "#222222", "#333333"]]
    lines = alien_json_to_text(grid)
    assert len(lines[-1]) == 3


def test_repeated_colors_reuse_the_same_character():
    grid = [["#AAAAAA", "#BBBBBB", "#AAAAAA"]]
    lines = alien_json_to_text(grid)
    row = lines[-1]
    assert row[0] == row[2]
    assert row[0] != row[1]


def test_too_many_colors_raises():
    grid = [[f"#{i:06X}" for i in range(53)]]
    with pytest.raises(ValueError):
        alien_json_to_text(grid)
