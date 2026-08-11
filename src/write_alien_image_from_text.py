import json
import sys
from pathlib import Path

from alien_text_to_json import alien_text_to_json
from image_painter import paint_image

if __name__ == "__main__":
    filename = sys.argv[1]

    with open(filename) as f:
        lines = [line.rstrip("\n") for line in f]

    alien = json.loads("\n".join(alien_text_to_json(lines)))

    output_filename = str(Path(filename).with_suffix(".png"))
    path = paint_image(data=alien, filename=output_filename)

    print(f"Alien generator: wrote {path}")
