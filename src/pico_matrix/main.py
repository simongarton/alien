"""Continuously generate random 16x16 aliens and display them on a WS2812B 16x16
addressable RGB matrix.

This is MicroPython, not CPython: it depends on the `machine` and `neopixel`
modules built into the Pico's MicroPython firmware (via pico_neopixel_matrix_driver),
so it will not run under `uv run` and has no access to `uv`-managed dependencies.
Copy this file, pico_neopixel_matrix_driver.py and alien_generator.py onto the Pico
(e.g. with Thonny or `mpremote cp`) and run it there:
    mpremote run pico_neopixel_alien_display.py

The matrix draws its own power from a separate 5V supply, wired to both the DIN
and mid-panel power-injection connectors, sharing a common ground with the Pico.
Only the DIN connector's data wire connects to the Pico (DATA_PIN in
pico_neopixel_matrix_driver.py).
"""

import time

from alien_generator import generate_alien
from pico_neopixel_matrix_driver import NeoPixelMatrix

REFRESH_SECONDS = 10
PAUSE_SECONDS = 2
BACKGROUND = "#000000"


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    return tuple(int(color[i : i + 2], 16) for i in (1, 3, 5))

def blank_screen(matrix: NeoPixelMatrix) -> None:
    for y in range(16):
        for x in range(16):
            matrix.set_pixel(x, y, _hex_to_rgb(BACKGROUND))
    matrix.show()


def draw_random_alien(matrix: NeoPixelMatrix) -> None:
    alien = generate_alien(
        width=matrix.width, height=matrix.height, background=BACKGROUND, palette="full", bigeyes=True, border=False
    )
    for y, row in enumerate(alien):
        for x, color in enumerate(row):
            matrix.set_pixel(x, y, _hex_to_rgb(color))
    matrix.show()


def main() -> None:
    matrix = NeoPixelMatrix()
    blank_screen(matrix)
    time.sleep(PAUSE_SECONDS)
    while True:
        draw_random_alien(matrix)
        time.sleep(REFRESH_SECONDS)
        blank_screen(matrix)
        time.sleep(PAUSE_SECONDS)


if __name__ == "__main__":
    main()
