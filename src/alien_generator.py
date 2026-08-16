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


def _body_mask(width: int, height: int, shape: str, border: bool = True) -> set[tuple[int, int]]:
    """Return the set of (row, col) cells inside the given shape, leaving room at the
    bottom for legs, the top for arms sticking up, and -- if border is True -- a
    margin on the sides and top so the body doesn't touch the edge of the grid.
    With border=False the body is free to fill the full width and top row, which
    matters on very small/low-resolution displays where every pixel counts. Each
    row's width is nudged by a random wobble factor so the silhouette isn't a
    perfectly clean shape."""
    bottom_margin = max(2, height // 4)
    top_margin = max(1, height // 8) if border else 0
    side_margin = max(1, width // 8) if border else 0
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


def _symmetric_mask(width: int, height: int, shape: str, border: bool = True) -> set[tuple[int, int]]:
    """Build the body mask on the left half, then mirror it onto the right half
    so the alien is left-right symmetric and solidly filled."""
    full_mask = _body_mask(width, height, shape, border=border)
    half_width = (width + 1) // 2

    result = set()
    for row, col in full_mask:
        if col >= half_width:
            continue
        result.add((row, col))
        mirror_col = width - 1 - col
        result.add((row, mirror_col))
    return result


def _eroded_mask(mask: set[tuple[int, int]], size: int) -> set[tuple[int, int]]:
    """Top-left positions where a size x size block, plus a 1-pixel margin all the
    way round it, lies entirely within mask -- i.e. where a block can be placed
    without touching a background cell."""
    safe = set()
    for r, c in mask:
        if all(
            (r + dr, c + dc) in mask
            for dr in range(-1, size + 1)
            for dc in range(-1, size + 1)
        ):
            safe.add((r, c))
    return safe


def _place_eyes(
    grid: list[list[str]],
    mask: set[tuple[int, int]],
    width: int,
    height: int,
    eyes: int,
    bigeyes: bool,
) -> set[tuple[int, int]]:
    """Paint eyes onto the grid, symmetric about the vertical centre line. Eyes are
    only ever placed where a ring of body colour surrounds them, so an eye never
    touches the background directly. Returns the set of cells consumed by eyes,
    so other features avoid them."""
    if not mask:
        return set()

    cx = (width - 1) / 2
    body_rows = sorted({row for row, _ in mask})
    target_row = body_rows[max(0, len(body_rows) // 4)]

    eye_size = 2 if bigeyes else 1
    safe = _eroded_mask(mask, eye_size)
    if not safe and eye_size == 2:
        # Fit guard: degrade to single-pixel eyes if there isn't room for a 2x2 block.
        eye_size = 1
        bigeyes = False
        safe = _eroded_mask(mask, eye_size)
    if not safe:
        return set()

    def mirror(col: int) -> int:
        return width - eye_size - col

    cols_by_row: dict[int, set[int]] = {}
    for row, col in safe:
        cols_by_row.setdefault(row, set()).add(col)
    ordered_rows = sorted(cols_by_row, key=lambda row: (abs(row - target_row), row))

    pair_offset = max(1, int(width * 0.2))
    desired_left = cx - pair_offset
    center_target = width / 2 - eye_size / 2

    def pick_pair(
        row_cols: set[int], desired: float, exclude: set[int], require_gap: bool
    ) -> tuple[int, int] | None:
        candidates = []
        for col in row_cols:
            twin = mirror(col)
            if twin not in row_cols or col > twin:
                continue
            # require_gap distinguishes two genuinely separate eyes (which must keep
            # at least a 1 pixel gap between them) from the centre "eye", which is
            # allowed to span both middle columns as a single feature when width is
            # even (there's no single centre pixel to sit on).
            if require_gap and twin != col and twin - (col + eye_size - 1) < 2:
                continue
            block = set(range(col, col + eye_size)) | set(range(twin, twin + eye_size))
            if block & exclude:
                continue
            candidates.append(col)
        if not candidates:
            return None
        best = min(candidates, key=lambda col: abs(col - desired))
        return best, mirror(best)

    eye_row = None
    final_cols: list[int] = []
    fallback: tuple[int, list[int]] | None = None
    for row in ordered_rows:
        row_cols = cols_by_row[row]
        outer = pick_pair(row_cols, desired_left, set(), require_gap=True)
        if outer is None:
            continue
        left_col, right_col = outer
        chosen = [left_col] if left_col == right_col else [left_col, right_col]

        if eyes != 3:
            eye_row, final_cols = row, chosen
            break

        # Buffer by 1 column on each side so the centre eye can't end up right
        # next to an outer eye either.
        occupied = set()
        for col in chosen:
            occupied.update(range(col - 1, col + eye_size + 1))
        center = pick_pair(row_cols, center_target, occupied, require_gap=False)
        if center is not None:
            cl, cr = center
            center_cols = [cl] if cl == cr else [cl, cr]
            eye_row, final_cols = row, center_cols + chosen
            break
        if fallback is None:
            fallback = (row, chosen)

    if eye_row is None:
        if fallback is None:
            return set()
        eye_row, final_cols = fallback

    # All eyes get their pupil in the same corner (left or right), chosen once,
    # rather than each eye pointing outward toward its own side.
    pupil_left = random.choice([True, False])

    consumed = set()
    for col in final_cols:
        for dr in range(eye_size):
            for dc in range(eye_size):
                r, c = eye_row + dr, col + dc
                grid[r][c] = EYE_COLOR
                consumed.add((r, c))

        if bigeyes:
            pupil_col = col if pupil_left else col + eye_size - 1
            grid[eye_row + eye_size - 1][pupil_col] = PUPIL_COLOR

    return consumed


MIN_LIMB_LENGTH = 2
MAX_LIMB_LENGTH = 5


def _select_limb_columns(half: list[int], width: int, pairs_needed: int) -> list[int]:
    """Choose up to pairs_needed columns from the left-half candidates, evenly
    spaced, skipping any column that would land a limb right next to an already
    chosen one (or its mirror on the other side) -- limbs always keep at least a
    1 pixel gap between them."""
    if not half or pairs_needed <= 0:
        return []

    def conflicts(col: int, chosen: list[int]) -> bool:
        mirror_col = width - 1 - col
        if mirror_col != col and abs(mirror_col - col) <= 1:
            return True
        return any(abs(col - c) <= 1 or abs(col - (width - 1 - c)) <= 1 for c in chosen)

    step = max(1, len(half) // pairs_needed)
    chosen: list[int] = []
    for col in half[::step]:
        if len(chosen) >= pairs_needed:
            break
        if not conflicts(col, chosen):
            chosen.append(col)

    if len(chosen) < pairs_needed:
        for col in half:
            if len(chosen) >= pairs_needed:
                break
            if col in chosen:
                continue
            if not conflicts(col, chosen):
                chosen.append(col)

    return chosen


def _paint_limb(
    grid: list[list[str]], col: int, edge: int, length: int, color: str, grow_down: bool, height: int
) -> None:
    for depth in range(1, length + 1):
        row = edge + depth if grow_down else edge - depth
        if 0 <= row < height:
            grid[row][col] = color


def _place_limbs(
    grid: list[list[str]],
    width: int,
    height: int,
    edge_by_col: dict[int, int],
    chosen_cols: list[int],
    count: int,
    color: str,
    grow_down: bool,
) -> None:
    """Paint up to `count` limbs from chosen_cols. A limb and its mirror are
    always added together (or, for a column on the centre line, as a single
    self-mirrored limb) so the result stays left-right symmetric, and a limb
    is only drawn when there's room for at least MIN_LIMB_LENGTH pixels."""
    remaining = count
    for col in chosen_cols:
        if remaining <= 0:
            break
        mirror_col = width - 1 - col
        edge = edge_by_col[col]
        available = height - 1 - edge if grow_down else edge
        max_len = min(MAX_LIMB_LENGTH, available)
        if max_len < MIN_LIMB_LENGTH:
            continue
        unit = 1 if mirror_col == col else 2
        if unit > remaining:
            continue

        length = random.randint(MIN_LIMB_LENGTH, max_len)
        _paint_limb(grid, col, edge, length, color, grow_down, height)
        remaining -= 1
        if mirror_col != col:
            mirror_edge = edge_by_col.get(mirror_col, edge)
            _paint_limb(grid, mirror_col, mirror_edge, length, color, grow_down, height)
            remaining -= 1


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
    chosen = _select_limb_columns(half, width, pairs_needed)
    _place_limbs(grid, width, height, body_bottom_by_col, chosen, legs, color, grow_down=True)


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
    chosen = _select_limb_columns(half, width, pairs_needed)
    _place_limbs(grid, width, height, body_top_by_col, chosen, arms, color, grow_down=False)


def generate_alien(
    width: int = 16,
    height: int = 16,
    background: str = "#ffffff",
    palette: str | list[str] = "cga",
    eyes: int = 2,
    bigeyes: bool = False,
    legs: int | None = None,
    arms: int = 0,
    shape: str | None = None,
    border: bool = True,
) -> list[list[str]]:
    """Generate an alien as a grid (list of rows) of hex colour strings. `palette`
    is either the name of a built-in palette, or an explicit list of hex colours
    to paint with. Set `border=False` to let the body fill the full width and top
    row of the grid -- useful for small displays (e.g. an 8x8 LED matrix) where
    the default margin would otherwise waste a large fraction of the pixels."""
    if legs is None:
        legs = random.randint(2, 5)
    if shape is None:
        shape = random.choice(SHAPES)

    colors = build_palette(palette, background) if isinstance(palette, str) else palette
    grid = [[background for _ in range(width)] for _ in range(height)]

    mask = _symmetric_mask(width, height, shape, border=border)
    body_color = random.choice(colors)
    for row, col in mask:
        grid[row][col] = body_color

    consumed = _place_eyes(grid, mask, width, height, eyes, bigeyes)
    feature_mask = mask - consumed

    _add_legs(grid, feature_mask, width, height, legs, body_color)
    _add_arms(grid, feature_mask, width, height, arms, body_color)

    return grid
