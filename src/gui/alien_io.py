"""Qt-free load/save helpers for the GUI, dispatching on file extension."""

import json
from pathlib import Path

from alien_json_to_text import alien_json_to_text
from alien_text_to_json import alien_text_to_json

SUPPORTED_EXTENSIONS = (".txt", ".json")


def load_alien(path: str) -> list[list[str]]:
    """Load an alien grid from a .json or .txt file."""
    suffix = Path(path).suffix.lower()
    if suffix == ".json":
        with open(path) as f:
            return json.load(f)
    if suffix == ".txt":
        with open(path) as f:
            lines = [line.rstrip("\n") for line in f]
        return json.loads("\n".join(alien_text_to_json(lines)))
    raise ValueError(f"Unsupported file extension: {suffix}")


def save_alien(path: str, grid: list[list[str]]) -> None:
    """Save an alien grid to a .json or .txt file."""
    suffix = Path(path).suffix.lower()
    if suffix == ".json":
        with open(path, "w") as f:
            json.dump(grid, f, indent=2)
        return
    if suffix == ".txt":
        lines = alien_json_to_text(grid)
        with open(path, "w") as f:
            f.write("\n".join(lines) + "\n")
        return
    raise ValueError(f"Unsupported file extension: {suffix}")


def new_grid(width: int, height: int, background: str) -> list[list[str]]:
    """Create a blank grid filled with the background colour."""
    return [[background for _ in range(width)] for _ in range(height)]


def derive_palette_and_background(grid: list[list[str]]) -> tuple[list[str], str]:
    """Derive a paintable palette and background colour for a loaded grid, which
    carries neither explicitly: the background is the most common colour, and the
    palette is every other distinct colour, in order of first appearance."""
    counts: dict[str, int] = {}
    for row in grid:
        for cell in row:
            counts[cell] = counts.get(cell, 0) + 1

    background = max(counts, key=counts.get)
    palette = [color for color in counts if color != background]
    if not palette:
        palette = [background]
    return palette, background
