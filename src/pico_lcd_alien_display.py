"""Continuously generate random 24x24 aliens and display them on a Waveshare Pico-LCD-1.14.

This is MicroPython, not CPython: it depends on the `machine` and `framebuf` modules
built into the Pico's MicroPython firmware (via pico_lcd_1_14_driver), so it will not
run under `uv run` and has no access to `uv`-managed dependencies. Copy this file,
pico_lcd_1_14_driver.py and alien_generator.py onto the Pico (e.g. with Thonny or
`mpremote cp`) and run it there:
    mpremote run pico_lcd_alien_display.py
"""

import random
import time

from alien_generator import generate_alien
from pico_lcd_1_14_driver import LCD_1inch14

ALIEN_SIZE = 24
REFRESH_SECONDS = 10
BACKGROUND = "#000000"


def _hex_to_rgb565(color: str) -> int:
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def draw_random_alien(lcd: LCD_1inch14) -> None:
    alien = generate_alien(
        width=ALIEN_SIZE, height=ALIEN_SIZE, background=BACKGROUND, palette="full", bigeyes=True
    )

    # Scale so the alien fills the screen height, then drop it at a random x offset.
    scale = lcd.height // ALIEN_SIZE
    scaled_size = ALIEN_SIZE * scale
    x_offset = random.randint(0, lcd.width - scaled_size)
    y_offset = (lcd.height - scaled_size) // 2

    lcd.fill(0)
    for row_index, row in enumerate(alien):
        for col_index, color in enumerate(row):
            if color.upper() == BACKGROUND.upper():
                continue
            lcd.fill_rect(
                x_offset + col_index * scale,
                y_offset + row_index * scale,
                scale,
                scale,
                _hex_to_rgb565(color),
            )
    lcd.show()


def main() -> None:
    lcd = LCD_1inch14()
    while True:
        draw_random_alien(lcd)
        time.sleep(REFRESH_SECONDS)


if __name__ == "__main__":
    main()
