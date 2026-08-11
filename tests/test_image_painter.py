from PIL import Image

from alien_generator import generate_alien
from image_painter import paint_image


def test_paint_image_default_filename(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    alien = generate_alien(width=4, height=4)
    path = paint_image(alien)
    assert path == "alien.png"
    assert (tmp_path / "alien.png").exists()


def test_paint_image_custom_filename(tmp_path):
    alien = generate_alien(width=4, height=4)
    filename = str(tmp_path / "custom.png")
    path = paint_image(alien, filename=filename)
    assert path == filename
    assert (tmp_path / "custom.png").exists()


def test_paint_image_size_matches_scale(tmp_path):
    alien = generate_alien(width=5, height=3)
    filename = str(tmp_path / "sized.png")
    paint_image(alien, filename=filename, scale=10)
    with Image.open(filename) as image:
        assert image.size == (50, 30)


def test_paint_image_pixel_colors_match_grid(tmp_path):
    alien = [["#FF0000", "#00FF00"], ["#0000FF", "#FFFFFF"]]
    filename = str(tmp_path / "colors.png")
    paint_image(alien, filename=filename, scale=2)
    with Image.open(filename) as image:
        assert image.getpixel((0, 0)) == (255, 0, 0)
        assert image.getpixel((2, 0)) == (0, 255, 0)
        assert image.getpixel((0, 2)) == (0, 0, 255)
        assert image.getpixel((2, 2)) == (255, 255, 255)
