"""Continuously generate random 8x8 aliens and display them on a Sense HAT.

Run on a Raspberry Pi (Zero or otherwise) with a Sense HAT attached:
    uv run python src/sense_hat_display.py
"""

import os
import time

from sense_hat import SenseHat

from alien_generator import generate_alien

REFRESH_SECONDS = float(os.environ.get("ALIEN_REFRESH_SECONDS", "10"))
BACKGROUND = os.environ.get("ALIEN_BACKGROUND", "#000000")
LOW_LIGHT = os.environ.get("ALIEN_LOW_LIGHT", "true").lower() == "true"


def _to_pixels(grid: list[list[str]]) -> list[tuple[int, int, int]]:
    """Flatten a row-major hex colour grid into the RGB tuple list set_pixels expects."""
    return [
        tuple(int(color[i : i + 2], 16) for i in (1, 3, 5))
        for row in grid
        for color in row
    ]


def show_random_alien(sense: SenseHat) -> None:
    # bigeyes forced on: at 8x8 single-pixel eyes are barely visible on the LED matrix.
    alien = generate_alien(width=8, height=8, background=BACKGROUND, palette="full", bigeyes=True)
    sense.set_pixels(_to_pixels(alien))


def main() -> None:
    sense = SenseHat()
    sense.low_light = LOW_LIGHT
    try:
        while True:
            show_random_alien(sense)
            time.sleep(REFRESH_SECONDS)
    except KeyboardInterrupt:
        sense.clear()


if __name__ == "__main__":
    main()
