import json
import sys
from pathlib import Path

from image_painter import paint_image

if __name__ == "__main__":
    filename = sys.argv[1]

    with open(filename) as f:
        alien = json.load(f)

    output_filename = str(Path(filename).with_suffix(".png"))
    path = paint_image(data=alien, filename=output_filename)

    print(f"Alien generator: wrote {path}")
