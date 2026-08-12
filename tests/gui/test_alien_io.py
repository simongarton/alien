import json

import pytest

from gui.alien_io import derive_palette_and_background, load_alien, new_grid, save_alien


def test_new_grid_dimensions_and_fill():
    grid = new_grid(width=3, height=2, background="#ABCDEF")
    assert len(grid) == 2
    assert all(len(row) == 3 for row in grid)
    assert all(cell == "#ABCDEF" for row in grid for cell in row)


def test_save_and_load_json_round_trip(tmp_path):
    grid = [["#FF0000", "#00FF00"], ["#0000FF", "#FFFFFF"]]
    path = str(tmp_path / "alien.json")

    save_alien(path, grid)
    loaded = load_alien(path)

    assert loaded == grid


def test_save_and_load_text_round_trip(tmp_path):
    grid = [["#FF0000", "#00FF00"], ["#0000FF", "#FFFFFF"]]
    path = str(tmp_path / "alien.txt")

    save_alien(path, grid)
    loaded = load_alien(path)

    assert loaded == grid


def test_saved_json_file_is_pretty_printed(tmp_path):
    grid = [["#000000"]]
    path = tmp_path / "alien.json"

    save_alien(str(path), grid)

    with open(path) as f:
        contents = f.read()
    assert json.loads(contents) == grid
    assert "\n" in contents


def test_saved_text_file_matches_expected_format(tmp_path):
    grid = [["#000000", "#0000FF"]]
    path = tmp_path / "alien.txt"

    save_alien(str(path), grid)

    with open(path) as f:
        lines = f.read().splitlines()
    assert lines == ["2", "A#000000", "B#0000FF", "1", "2", "AB"]


def test_load_unsupported_extension_raises(tmp_path):
    path = tmp_path / "alien.png"
    path.write_text("not an alien file")

    with pytest.raises(ValueError):
        load_alien(str(path))


def test_save_unsupported_extension_raises(tmp_path):
    path = tmp_path / "alien.png"

    with pytest.raises(ValueError):
        save_alien(str(path), [["#000000"]])


def test_derive_picks_most_common_color_as_background():
    grid = [
        ["#FFFFFF", "#FFFFFF", "#FF0000"],
        ["#FFFFFF", "#00FF00", "#FFFFFF"],
    ]
    palette, background = derive_palette_and_background(grid)
    assert background == "#FFFFFF"
    assert set(palette) == {"#FF0000", "#00FF00"}


def test_derive_excludes_background_from_palette():
    grid = [["#000000", "#000000", "#FFFFFF"]]
    palette, background = derive_palette_and_background(grid)
    assert background == "#000000"
    assert "#000000" not in palette


def test_derive_falls_back_to_background_only_palette_for_uniform_grid():
    grid = [["#123456", "#123456"], ["#123456", "#123456"]]
    palette, background = derive_palette_and_background(grid)
    assert background == "#123456"
    assert palette == ["#123456"]


def test_derive_palette_order_matches_first_appearance():
    grid = [["#FFFFFF", "#00FF00", "#0000FF"], ["#FF0000", "#FFFFFF", "#FFFFFF"]]
    palette, background = derive_palette_and_background(grid)
    assert background == "#FFFFFF"
    assert palette == ["#00FF00", "#0000FF", "#FF0000"]
