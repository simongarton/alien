"""Convert an alien grid in the Text file format into the JSON file format."""

import json


def alien_text_to_json(lines: list[str]) -> list[str]:
    """Convert the lines of the Text file format into the lines of the JSON
    file format: parse the colour count, the colour-to-character mapping, the
    height and width, and the pixel rows, then re-encode the resulting grid
    as pretty-printed JSON."""
    num_colors = int(lines[0])

    color_map: dict[str, str] = {}
    for line in lines[1 : 1 + num_colors]:
        char, hex_code = line[0], line[1:]
        color_map[char] = hex_code

    header_index = 1 + num_colors
    height = int(lines[header_index])
    width = int(lines[header_index + 1])

    rows_start = header_index + 2
    grid: list[list[str]] = []
    for row_line in lines[rows_start : rows_start + height]:
        grid.append([color_map[char] for char in row_line[:width]])

    return json.dumps(grid, indent=2).splitlines()
