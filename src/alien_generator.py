"""Generate alien DNA into a pixel grid of hex colours."""

import random

CGA_PALETTE = [
    "#000000", "#0000AA", "#00AA00", "#00AAAA",
    "#AA0000", "#AA00AA", "#AA5500", "#AAAAAA",
    "#555555", "#5555FF", "#55FF55", "#55FFFF",
    "#FF5555", "#FF55FF", "#FFFF55", "#FFFFFF",
]

SHADE_PALETTES = {
    "green": ("#006400", "#00FF00"),
    "red": ("#640000", "#FF0000"),
    "blue": ("#000064", "#0000FF"),
}

SHAPES = ["circle", "oval", "square", "triangle", "triangle_inverted"]

EYE_COLOR = "#FFFFFF"
PUPIL_COLOR = "#000000"


def _interpolate(start_hex: str, end_hex: str, steps: int) -> list[str]:
    start = tuple(int(start_hex[i : i + 2], 16) for i in (1, 3, 5))
    end = tuple(int(end_hex[i : i + 2], 16) for i in (1, 3, 5))
    colors = []
    for step in range(steps):
        ratio = step / max(steps - 1, 1)
        rgb = tuple(round(s + (e - s) * ratio) for s, e in zip(start, end))
        colors.append("#{:02X}{:02X}{:02X}".format(*rgb))
    return colors


def build_palette(name: str, background: str) -> list[str]:
    """Build the list of usable body colours for a palette, excluding the background."""
    if name == "cga":
        colors = list(CGA_PALETTE)
    elif name in SHADE_PALETTES:
        colors = _interpolate(*SHADE_PALETTES[name], steps=16)
    elif name == "full":
        colors = [
            f"#{random.randint(0, 255):02X}{random.randint(0, 255):02X}{random.randint(0, 255):02X}"
            for _ in range(64)
        ]
    else:
        raise ValueError(f"Unknown palette: {name}")

    background_upper = background.upper()
    colors = [c for c in colors if c.upper() != background_upper]
    if not colors:
        raise ValueError(f"Palette '{name}' has no colours left after excluding background {background}")
    return colors


WOBBLE_RANGE = (0.85, 1.05)


def _body_mask(width: int, height: int, shape: str) -> set[tuple[int, int]]:
    """Return the set of (row, col) cells inside the given shape, leaving room at the
    bottom for legs, the top for arms sticking up, and a border on all sides so the
    body never touches the edge of the grid. Each row's width is nudged by a random
    wobble factor so the silhouette isn't a perfectly clean shape."""
    top_margin = max(1, height // 8)
    bottom_margin = max(2, height // 4)
    side_margin = max(1, width // 8)
    body_top = top_margin
    body_bottom = height - bottom_margin
    body_left = side_margin
    body_right = max(body_left + 1, width - side_margin)
    body_height = max(1, body_bottom - body_top)
    body_width = max(1, body_right - body_left)

    cx = (body_left + body_right - 1) / 2
    cy = body_top + (body_height - 1) / 2
    rx = body_width / 2
    ry = body_height / 2

    mask = set()
    for row in range(body_top, body_bottom):
        wobble = random.uniform(*WOBBLE_RANGE)
        row_rx = rx * wobble
        for col in range(body_left, body_right):
            dx = (col - cx) / row_rx if row_rx else 0
            dy = (row - cy) / ry if ry else 0
            if shape == "circle":
                inside = dx * dx + dy * dy <= 1.0
            elif shape == "oval":
                inside = (dx * dx) / 1.0 + (dy * dy) / 0.6 <= 1.0
            elif shape == "square":
                inside = abs(col - cx) <= row_rx
            elif shape == "triangle":
                row_ratio = (row - body_top) / max(body_height - 1, 1)
                half_width = row_ratio * row_rx
                inside = abs(col - cx) <= half_width
            elif shape == "triangle_inverted":
                row_ratio = (row - body_top) / max(body_height - 1, 1)
                half_width = (1 - row_ratio) * row_rx
                inside = abs(col - cx) <= half_width
            else:
                raise ValueError(f"Unknown shape: {shape}")
            if inside:
                mask.add((row, col))
    return mask


def _symmetric_mask(width: int, height: int, shape: str) -> set[tuple[int, int]]:
    """Build the body mask on the left half, then mirror it onto the right half
    so the alien is left-right symmetric and solidly filled."""
    full_mask = _body_mask(width, height, shape)
    half_width = (width + 1) // 2

    result = set()
    for row, col in full_mask:
        if col >= half_width:
            continue
        result.add((row, col))
        mirror_col = width - 1 - col
        result.add((row, mirror_col))
    return result


def _place_eyes(
    grid: list[list[str]],
    mask: set[tuple[int, int]],
    width: int,
    height: int,
    eyes: int,
    bigeyes: bool,
) -> set[tuple[int, int]]:
    """Paint eyes onto the grid, symmetric about the vertical centre line.
    Returns the set of cells consumed by eyes, so other features avoid them."""
    if not mask:
        return set()

    body_rows = sorted({row for row, _ in mask})
    eye_row = body_rows[max(0, len(body_rows) // 4)]
    cx = (width - 1) / 2
    consumed = set()

    eye_size = 2 if bigeyes else 1
    # Fit guard: degrade to single-pixel eyes if there isn't room for a 2x2 block.
    if bigeyes and (eye_row + 1 >= height or width < 4):
        eye_size = 1
        bigeyes = False

    pair_offset = max(1, int(width * 0.2))
    left_col = round(cx - pair_offset)
    right_col = width - 1 - left_col  # mirror of left_col, not independently rounded
    # Centre "eye" spans both middle columns so it mirrors itself even when width
    # is even (there is no single centre pixel): floor(cx) and ceil(cx) are always
    # mirror images of each other, collapsing to one column when width is odd.
    center_cols = sorted({width // 2 - (1 if width % 2 == 0 else 0), width // 2})

    cols = [left_col, right_col]
    if eyes == 3:
        cols = center_cols + cols

    if eye_row + eye_size - 1 >= height:
        return consumed

    for col in cols:
        if col < 0 or col + eye_size - 1 >= width:
            continue

        for dr in range(eye_size):
            for dc in range(eye_size):
                r, c = eye_row + dr, col + dc
                grid[r][c] = EYE_COLOR
                consumed.add((r, c))

        if bigeyes:
            is_left_half = col < cx
            pupil_col = col if is_left_half else col + eye_size - 1
            grid[eye_row + eye_size - 1][pupil_col] = PUPIL_COLOR

    return consumed


def _add_legs(grid: list[list[str]], mask: set[tuple[int, int]], width: int, height: int, legs: int, color: str) -> None:
    if legs <= 0 or not mask:
        return
    body_bottom_by_col: dict[int, int] = {}
    for row, col in mask:
        body_bottom_by_col[col] = max(body_bottom_by_col.get(col, row), row)
    candidate_cols = sorted(body_bottom_by_col)
    if not candidate_cols:
        return

    cx = (width - 1) / 2
    half = sorted({c for c in candidate_cols if c <= cx})
    if not half:
        half = candidate_cols[: max(1, len(candidate_cols) // 2)]

    pairs_needed = (legs + 1) // 2
    step = max(1, len(half) // max(pairs_needed, 1))
    chosen = half[::step][:pairs_needed]

    placed = 0
    for col in chosen:
        if placed >= legs:
            break
        bottom = body_bottom_by_col[col]
        # Both sides of a mirrored pair share the same random length, since their
        # body_bottom is identical (the mask is already left-right symmetric).
        max_len = height - 1 - bottom
        length = random.randint(1, max_len) if max_len > 0 else 0
        for depth in range(1, length + 1):
            grid[bottom + depth][col] = color
        mirror_col = width - 1 - col
        placed += 1
        if placed >= legs and mirror_col == col:
            break
        if mirror_col != col and placed < legs:
            mirror_bottom = body_bottom_by_col.get(mirror_col, bottom)
            for depth in range(1, length + 1):
                if mirror_bottom + depth < height:
                    grid[mirror_bottom + depth][mirror_col] = color
            placed += 1


def _add_arms(grid: list[list[str]], mask: set[tuple[int, int]], width: int, height: int, arms: int, color: str) -> None:
    if arms <= 0 or not mask:
        return
    body_top_by_col: dict[int, int] = {}
    for row, col in mask:
        body_top_by_col[col] = min(body_top_by_col.get(col, row), row)
    candidate_cols = sorted(body_top_by_col)
    if not candidate_cols:
        return

    cx = (width - 1) / 2
    half = sorted({c for c in candidate_cols if c <= cx})
    if not half:
        half = candidate_cols[: max(1, len(candidate_cols) // 2)]

    pairs_needed = (arms + 1) // 2
    step = max(1, len(half) // max(pairs_needed, 1))
    chosen = half[::step][:pairs_needed]

    placed = 0
    for col in chosen:
        if placed >= arms:
            break
        top = body_top_by_col[col]
        # Both sides of a mirrored pair share the same random length, since their
        # body_top is identical (the mask is already left-right symmetric).
        max_len = top
        length = random.randint(1, max_len) if max_len > 0 else 0
        for depth in range(1, length + 1):
            grid[top - depth][col] = color
        mirror_col = width - 1 - col
        placed += 1
        if placed >= arms:
            break
        if mirror_col != col:
            mirror_top = body_top_by_col.get(mirror_col, top)
            for depth in range(1, length + 1):
                if mirror_top - depth >= 0:
                    grid[mirror_top - depth][mirror_col] = color
            placed += 1


def generate_alien(
    width: int = 16,
    height: int = 16,
    background: str = "#ffffff",
    palette: str = "cga",
    eyes: int = 2,
    bigeyes: bool = False,
    legs: int | None = None,
    arms: int = 0,
    shape: str | None = None,
) -> list[list[str]]:
    """Generate an alien as a grid (list of rows) of hex colour strings."""
    if legs is None:
        legs = random.randint(2, 5)
    if shape is None:
        shape = random.choice(SHAPES)

    colors = build_palette(palette, background)
    grid = [[background for _ in range(width)] for _ in range(height)]

    mask = _symmetric_mask(width, height, shape)
    body_color = random.choice(colors)
    for row, col in mask:
        grid[row][col] = body_color

    consumed = _place_eyes(grid, mask, width, height, eyes, bigeyes)
    feature_mask = mask - consumed

    limb_color = random.choice(colors)
    _add_legs(grid, feature_mask, width, height, legs, limb_color)
    _add_arms(grid, feature_mask, width, height, arms, limb_color)

    return grid
