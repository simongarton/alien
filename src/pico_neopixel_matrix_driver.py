"""Thin wrapper around MicroPython's built-in `neopixel` module for a 16x16 WS2812B
addressable RGB matrix.

MicroPython only: depends on `machine.Pin` and `neopixel.NeoPixel`, which are built
into the Pico's MicroPython firmware. Will not run under `uv run`/CPython.
"""

from machine import Pin
from neopixel import NeoPixel

DATA_PIN = 0
MAX_BRIGHTNESS = 0.1


class NeoPixelMatrix:
    """A row-major (x, y) view onto a WS2812B panel wired in serpentine order --
    row 0 left-to-right, row 1 right-to-left, and so on. That's how almost all of
    these panels are wired, but it hasn't been confirmed against this specific
    panel yet; if the alien comes out shredded into diagonal stripes, set
    `serpentine=False` and try again, and if that's also wrong use `debug_scan()`
    to watch the real pixel order and fix `_index()` to match.
    """

    def __init__(
        self,
        width: int = 16,
        height: int = 16,
        pin: int = DATA_PIN,
        brightness: float = MAX_BRIGHTNESS,
        serpentine: bool = True,
    ) -> None:
        self.width = width
        self.height = height
        self.brightness = brightness
        self.serpentine = serpentine
        self.np = NeoPixel(Pin(pin, Pin.OUT), width * height)

    def _index(self, x: int, y: int) -> int:
        if self.serpentine and y % 2 == 1:
            x = self.width - 1 - x
        return y * self.width + x

    def set_pixel(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        r, g, b = color
        scale = self.brightness
        self.np[self._index(x, y)] = (int(r * scale), int(g * scale), int(b * scale))

    def fill(self, color: tuple[int, int, int] = (0, 0, 0)) -> None:
        for i in range(len(self.np)):
            self.np[i] = color

    def show(self) -> None:
        self.np.write()

    def debug_scan(self, delay_ms: int = 150) -> None:
        """Light pixels one at a time in raw strip order (index 0, 1, 2, ...),
        ignoring the (x, y) mapping, so you can watch the real wiring order on
        the panel and confirm/fix `serpentine` and `_index()` above."""
        import time

        self.fill((0, 0, 0))
        self.show()
        for i in range(len(self.np)):
            self.np[i] = (40, 0, 0)
            self.show()
            time.sleep_ms(delay_ms)
            self.np[i] = (0, 0, 0)
