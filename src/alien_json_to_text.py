"""Convert an alien grid (the JSON format) into the Text file format."""

import string

CHAR_POOL = string.ascii_uppercase + string.ascii_lowercase


def alien_json_to_text(grid: list[list[str]]) -> list[str]:
    """Convert an alien grid (list of rows of hex colours) into the lines of
    the Text file format: a colour count, one line per colour mapping a
    single character to its hex code, the height, the width, and then one
    line per row using those characters."""
    height = len(grid)
    width = len(grid[0]) if height else 0

    colors: list[str] = []
    seen: set[str] = set()
    for row in grid:
        for cell in row:
            if cell not in seen:
                seen.add(cell)
                colors.append(cell)

    if len(colors) > len(CHAR_POOL):
        raise ValueError(f"Too many distinct colours ({len(colors)}) for the Text format")

    color_to_char = {color: CHAR_POOL[i] for i, color in enumerate(colors)}

    lines = [str(len(colors))]
    lines.extend(f"{color_to_char[color]}{color}" for color in colors)
    lines.append(str(height))
    lines.append(str(width))
    lines.extend("".join(color_to_char[cell] for cell in row) for row in grid)

    return lines
