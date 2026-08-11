"""Paint an alien pixel grid (as produced by alien_generator.generate_alien) to a PNG."""

from PIL import Image


def paint_image(alien: list[list[str]], filename: str = "alien.png", scale: int = 20) -> str:
    """Render a grid of hex colours to a PNG file. Each grid cell is drawn as a
    scale x scale block of pixels so small aliens are still viewable."""
    height = len(alien)
    width = len(alien[0]) if height else 0

    image = Image.new("RGB", (width * scale, height * scale))
    pixels = image.load()

    for row in range(height):
        for col in range(width):
            color = alien[row][col]
            rgb = tuple(int(color[i : i + 2], 16) for i in (1, 3, 5))
            for dy in range(scale):
                for dx in range(scale):
                    pixels[col * scale + dx, row * scale + dy] = rgb

    image.save(filename)
    return filename
