import json

from alien_json_to_text import alien_json_to_text
from alien_text_to_json import alien_text_to_json


def test_matches_example_format():
    lines = [
        "3",
        "B#000000",
        "b#0000FF",
        "W#FFFFFF",
        "4",
        "8",
        "BBBBBBBB",
        "BBBbbBBB",
        "BBbbbbBB",
        "BbWbbWbB",
    ]
    grid = json.loads("\n".join(alien_text_to_json(lines)))
    assert grid == [
        ["#000000"] * 8,
        ["#000000", "#000000", "#000000", "#0000FF", "#0000FF", "#000000", "#000000", "#000000"],
        ["#000000", "#000000", "#0000FF", "#0000FF", "#0000FF", "#0000FF", "#000000", "#000000"],
        ["#000000", "#0000FF", "#FFFFFF", "#0000FF", "#0000FF", "#FFFFFF", "#0000FF", "#000000"],
    ]


def test_round_trips_through_json_to_text():
    lines = [
        "2",
        "A#123456",
        "B#654321",
        "2",
        "2",
        "AB",
        "BA",
    ]
    grid = json.loads("\n".join(alien_text_to_json(lines)))
    assert alien_json_to_text(grid) == lines


def test_output_is_valid_json():
    lines = ["1", "X#010203", "1", "1", "X"]
    result = alien_text_to_json(lines)
    assert isinstance(result, list)
    assert all(isinstance(line, str) for line in result)
    assert json.loads("\n".join(result)) == [["#010203"]]
