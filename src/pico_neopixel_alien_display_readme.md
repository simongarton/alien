This is a second, separate Pico from the one running `pico_lcd_alien_display.py` --
it drives a 16x16 WS2812B addressable RGB matrix instead of the Pico-LCD-1.14.

Whatever is in `pico_neopixel_alien_display.py` should be copied to
`pico_matrix/main.py` and then copied across to this second Pico, along with
`pico_neopixel_matrix_driver.py` and `alien_generator.py`.

I am trying to keep the main `alien_generator.py` untouched.

## Wiring

- Matrix DIN connector's data wire -> Pico `DATA_PIN` (GP0 by default, see
  `pico_neopixel_matrix_driver.py`).
- Matrix DIN and mid-panel connectors' 5V/GND -> a separate 5V supply (NOT the
  Pico), wired in parallel. The Pico is powered independently (USB).
- Matrix GND -> also tied to a Pico GND pin, so the data signal has a common
  reference with the panel's power rail.
- DOUT connector is unused (no second panel chained on).

## If the alien looks scrambled

`NeoPixelMatrix` assumes the panel is wired in the usual serpentine order (row 0
left-to-right, row 1 right-to-left, alternating). That's unconfirmed against this
specific panel. If the displayed alien comes out as diagonal noise instead of a
recognisable shape:
- try `NeoPixelMatrix(serpentine=False)` first,
- if that's also wrong, call `.debug_scan()` from the MicroPython REPL to watch
  pixels light up in raw strip order and fix `_index()` in
  `pico_neopixel_matrix_driver.py` to match what you see.
