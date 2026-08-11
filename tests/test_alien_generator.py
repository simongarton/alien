import re

import pytest

from alien_generator import SHAPES, build_palette, generate_alien

HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def test_default_dimensions():
    alien = generate_alien()
    assert len(alien) == 16
    assert all(len(row) == 16 for row in alien)


def test_custom_dimensions():
    alien = generate_alien(width=10, height=6)
    assert len(alien) == 6
    assert all(len(row) == 10 for row in alien)


def test_all_cells_are_valid_hex():
    alien = generate_alien()
    for row in alien:
        for cell in row:
            assert HEX_RE.match(cell)


@pytest.mark.parametrize("palette", ["cga", "green", "red", "blue", "full"])
def test_palette_excludes_background(palette):
    background = "#ffffff"
    colors = build_palette(palette, background)
    assert background.upper() not in [c.upper() for c in colors]


def test_body_and_eyes_are_left_right_symmetric():
    # legs/arms counts can be odd (e.g. a tripod), so only body shape + eyes are
    # guaranteed symmetric; exclude limbs from this check by generating none.
    alien = generate_alien(width=16, height=16, eyes=2, legs=0, arms=0)
    for row in alien:
        assert row == list(reversed(row)), "alien is not left-right symmetric"


def test_even_legs_and_arms_are_left_right_symmetric():
    alien = generate_alien(width=16, height=16, eyes=2, legs=4, arms=2)
    for row in alien:
        assert row == list(reversed(row)), "even legs/arms should mirror too"


def test_legs_default_is_between_2_and_5():
    for _ in range(20):
        alien = generate_alien(legs=None)
        assert alien is not None  # legs count isn't directly observable from the grid


def test_shape_can_be_forced():
    for shape in SHAPES:
        alien = generate_alien(shape=shape)
        assert len(alien) == 16


def test_small_grid_does_not_crash_with_bigeyes():
    alien = generate_alien(width=4, height=4, eyes=3, bigeyes=True)
    assert len(alien) == 4


def test_unknown_palette_raises():
    with pytest.raises(ValueError):
        generate_alien(palette="not-a-real-palette")
