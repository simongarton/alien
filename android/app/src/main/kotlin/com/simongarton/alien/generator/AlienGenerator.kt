package com.simongarton.alien.generator

import kotlin.math.abs
import kotlin.random.Random

val CGA_PALETTE =
    listOf(
        "#000000",
        "#0000AA",
        "#00AA00",
        "#00AAAA",
        "#AA0000",
        "#AA00AA",
        "#AA5500",
        "#AAAAAA",
        "#555555",
        "#5555FF",
        "#55FF55",
        "#55FFFF",
        "#FF5555",
        "#FF55FF",
        "#FFFF55",
        "#FFFFFF",
    )

private val SHADE_PALETTES =
    mapOf(
        "green" to ("#006400" to "#00FF00"),
        "red" to ("#640000" to "#FF0000"),
        "blue" to ("#000064" to "#0000FF"),
    )

val PALETTE_NAMES = listOf("cga", "green", "red", "blue", "full")

private val SHAPES = listOf("circle", "oval", "square", "triangle", "triangle_inverted")

private const val EYE_COLOR = "#FFFFFF"
private const val PUPIL_COLOR = "#000000"

private fun interpolate(
    startHex: String,
    endHex: String,
    steps: Int,
): List<String> {
    fun channels(hex: String) = (0..2).map { i -> hex.substring(1 + i * 2, 3 + i * 2).toInt(16) }
    val start = channels(startHex)
    val end = channels(endHex)
    return (0 until steps).map { step ->
        val ratio = step.toDouble() / maxOf(steps - 1, 1)
        val rgb = start.zip(end).map { (s, e) -> Math.round(s + (e - s) * ratio).toInt() }
        "#%02X%02X%02X".format(rgb[0], rgb[1], rgb[2])
    }
}

private const val MIN_BACKGROUND_DISTANCE = 60.0

private fun hexToRgb(hex: String): Triple<Int, Int, Int> =
    Triple(
        hex.substring(1, 3).toInt(16),
        hex.substring(3, 5).toInt(16),
        hex.substring(5, 7).toInt(16),
    )

private fun colorDistance(
    a: String,
    b: String,
): Double {
    val (ar, ag, ab) = hexToRgb(a)
    val (br, bg, bb) = hexToRgb(b)
    val dr = (ar - br).toDouble()
    val dg = (ag - bg).toDouble()
    val db = (ab - bb).toDouble()
    return kotlin.math.sqrt(dr * dr + dg * dg + db * db)
}

/**
 * Build the list of usable body colours for a palette, excluding the background and anything
 * close enough to it (e.g. a near-black colour from the `full` palette against a black
 * background) to be effectively invisible against it.
 */
fun buildPalette(
    name: String,
    background: String,
    random: Random,
): List<String> {
    val colors =
        when {
            name == "cga" -> CGA_PALETTE
            SHADE_PALETTES.containsKey(name) -> {
                val (start, end) = SHADE_PALETTES.getValue(name)
                interpolate(start, end, 16)
            }
            name == "full" ->
                (0 until 64).map {
                    "#%02X%02X%02X".format(random.nextInt(256), random.nextInt(256), random.nextInt(256))
                }
            else -> throw IllegalArgumentException("Unknown palette: $name")
        }

    val backgroundUpper = background.uppercase()
    val filtered = colors.filter { it.uppercase() != backgroundUpper }
    val visible = filtered.filter { colorDistance(it, background) >= MIN_BACKGROUND_DISTANCE }
    val result = visible.ifEmpty { filtered }
    require(result.isNotEmpty()) { "Palette '$name' has no colours left after excluding background $background" }
    return result
}

private const val WOBBLE_MIN = 0.85
private const val WOBBLE_MAX = 1.05

/**
 * Return the set of (row, col) cells inside the given shape, leaving room at the bottom for
 * legs, the top for arms sticking up, and -- if border is true -- a margin on the sides and top
 * so the body doesn't touch the edge of the grid. Each row's width is nudged by a random wobble
 * factor so the silhouette isn't a perfectly clean shape.
 */
private fun bodyMask(
    width: Int,
    height: Int,
    shape: String,
    border: Boolean,
    random: Random,
): Set<Pair<Int, Int>> {
    val bottomMargin = maxOf(2, height / 4)
    val topMargin = if (border) maxOf(1, height / 8) else 0
    val sideMargin = if (border) maxOf(1, width / 8) else 0
    val bodyTop = topMargin
    val bodyBottom = height - bottomMargin
    val bodyLeft = sideMargin
    val bodyRight = maxOf(bodyLeft + 1, width - sideMargin)
    val bodyHeight = maxOf(1, bodyBottom - bodyTop)
    val bodyWidth = maxOf(1, bodyRight - bodyLeft)

    val cx = (bodyLeft + bodyRight - 1) / 2.0
    val cy = bodyTop + (bodyHeight - 1) / 2.0
    val rx = bodyWidth / 2.0
    val ry = bodyHeight / 2.0

    val mask = mutableSetOf<Pair<Int, Int>>()
    for (row in bodyTop until bodyBottom) {
        val wobble = WOBBLE_MIN + random.nextDouble() * (WOBBLE_MAX - WOBBLE_MIN)
        val rowRx = rx * wobble
        for (col in bodyLeft until bodyRight) {
            val dx = if (rowRx != 0.0) (col - cx) / rowRx else 0.0
            val dy = if (ry != 0.0) (row - cy) / ry else 0.0
            val inside =
                when (shape) {
                    "circle" -> dx * dx + dy * dy <= 1.0
                    "oval" -> (dx * dx) / 1.0 + (dy * dy) / 0.6 <= 1.0
                    "square" -> abs(col - cx) <= rowRx
                    "triangle" -> {
                        val rowRatio = (row - bodyTop) / maxOf(bodyHeight - 1, 1).toDouble()
                        abs(col - cx) <= rowRatio * rowRx
                    }
                    "triangle_inverted" -> {
                        val rowRatio = (row - bodyTop) / maxOf(bodyHeight - 1, 1).toDouble()
                        abs(col - cx) <= (1 - rowRatio) * rowRx
                    }
                    else -> throw IllegalArgumentException("Unknown shape: $shape")
                }
            if (inside) mask.add(row to col)
        }
    }
    return mask
}

/** Build the body mask on the left half, then mirror it onto the right half. */
private fun symmetricMask(
    width: Int,
    height: Int,
    shape: String,
    border: Boolean,
    random: Random,
): Set<Pair<Int, Int>> {
    val fullMask = bodyMask(width, height, shape, border, random)
    val halfWidth = (width + 1) / 2

    val result = mutableSetOf<Pair<Int, Int>>()
    for ((row, col) in fullMask) {
        if (col >= halfWidth) continue
        result.add(row to col)
        result.add(row to (width - 1 - col))
    }
    return result
}

/**
 * Top-left positions where a size x size block, plus a 1-pixel margin all the way round it,
 * lies entirely within mask -- i.e. where a block can be placed without touching a background cell.
 */
private fun erodedMask(
    mask: Set<Pair<Int, Int>>,
    size: Int,
): Set<Pair<Int, Int>> {
    val safe = mutableSetOf<Pair<Int, Int>>()
    for ((r, c) in mask) {
        var ok = true
        loop@ for (dr in -1..size) {
            for (dc in -1..size) {
                if ((r + dr) to (c + dc) !in mask) {
                    ok = false
                    break@loop
                }
            }
        }
        if (ok) safe.add(r to c)
    }
    return safe
}

/**
 * Paint eyes onto the grid, symmetric about the vertical centre line. Eyes are only ever placed
 * where a ring of body colour surrounds them, so an eye never touches the background directly.
 * Returns the set of cells consumed by eyes, so other features avoid them.
 */
private fun placeEyes(
    grid: Array<Array<String>>,
    mask: Set<Pair<Int, Int>>,
    width: Int,
    eyes: Int,
    bigEyesParam: Boolean,
    shape: String?,
    random: Random,
): Set<Pair<Int, Int>> {
    if (mask.isEmpty()) return emptySet()

    val cx = (width - 1) / 2.0
    val bodyRows = mask.map { it.first }.distinct().sorted()
    // A plain "triangle" body is narrowest at the top, so eyes are more likely to fit if we look
    // near the bottom instead of the usual near-the-top target row.
    val targetRow =
        if (shape == "triangle") {
            bodyRows[minOf(bodyRows.size - 1, (3 * bodyRows.size) / 4)]
        } else {
            bodyRows[maxOf(0, bodyRows.size / 4)]
        }

    var eyeSize = if (bigEyesParam) 2 else 1
    var bigEyes = bigEyesParam
    var safe = erodedMask(mask, eyeSize)
    if (safe.isEmpty() && eyeSize == 2) {
        // Fit guard: degrade to single-pixel eyes if there isn't room for a 2x2 block.
        eyeSize = 1
        bigEyes = false
        safe = erodedMask(mask, eyeSize)
    }
    if (safe.isEmpty()) return emptySet()

    fun mirror(col: Int) = width - eyeSize - col

    val colsByRow = mutableMapOf<Int, MutableSet<Int>>()
    for ((row, col) in safe) {
        colsByRow.getOrPut(row) { mutableSetOf() }.add(col)
    }
    val orderedRows = colsByRow.keys.sortedWith(compareBy({ abs(it - targetRow) }, { it }))

    val pairOffset = maxOf(1, (width * 0.2).toInt())
    val desiredLeft = cx - pairOffset
    val centerTarget = width / 2.0 - eyeSize / 2.0

    fun pickPair(
        rowCols: Set<Int>,
        desired: Double,
        exclude: Set<Int>,
        requireGap: Boolean,
    ): Pair<Int, Int>? {
        // requireGap distinguishes two genuinely separate eyes (which must keep at least a
        // 1 pixel gap between them) from the centre "eye", which is allowed to span both middle
        // columns as a single feature when width is even (there's no single centre pixel to sit on).
        val candidates = mutableListOf<Int>()
        for (col in rowCols) {
            val twin = mirror(col)
            if (twin !in rowCols || col > twin) continue
            if (requireGap && twin != col && twin - (col + eyeSize - 1) < 2) continue
            val block = (col until col + eyeSize).toSet() + (twin until twin + eyeSize).toSet()
            if (block.any { it in exclude }) continue
            candidates.add(col)
        }
        if (candidates.isEmpty()) return null
        val best = candidates.minByOrNull { abs(it - desired) }!!
        return best to mirror(best)
    }

    var eyeRow: Int? = null
    var finalCols: List<Int> = emptyList()
    var fallback: Pair<Int, List<Int>>? = null

    for (row in orderedRows) {
        val rowCols = colsByRow.getValue(row)
        val outer = pickPair(rowCols, desiredLeft, emptySet(), requireGap = true) ?: continue
        val (leftCol, rightCol) = outer
        val chosen = if (leftCol == rightCol) listOf(leftCol) else listOf(leftCol, rightCol)

        if (eyes != 3) {
            eyeRow = row
            finalCols = chosen
            break
        }

        // Buffer by 1 column on each side so the centre eye can't end up right next to an outer eye either.
        val occupied = mutableSetOf<Int>()
        for (col in chosen) occupied.addAll(col - 1 until col + eyeSize + 1)
        val center = pickPair(rowCols, centerTarget, occupied, requireGap = false)
        if (center != null) {
            val (cl, cr) = center
            val centerCols = if (cl == cr) listOf(cl) else listOf(cl, cr)
            eyeRow = row
            finalCols = centerCols + chosen
            break
        }
        if (fallback == null) fallback = row to chosen
    }

    val resolvedRow: Int
    val resolvedCols: List<Int>
    if (eyeRow != null) {
        resolvedRow = eyeRow
        resolvedCols = finalCols
    } else {
        val fb = fallback ?: return emptySet()
        resolvedRow = fb.first
        resolvedCols = fb.second
    }

    // All eyes get their pupil in the same corner (left or right), chosen once, rather than each
    // eye pointing outward toward its own side.
    val pupilLeft = random.nextBoolean()

    val consumed = mutableSetOf<Pair<Int, Int>>()
    for (col in resolvedCols) {
        for (dr in 0 until eyeSize) {
            for (dc in 0 until eyeSize) {
                val r = resolvedRow + dr
                val c = col + dc
                grid[r][c] = EYE_COLOR
                consumed.add(r to c)
            }
        }
        if (bigEyes) {
            val pupilCol = if (pupilLeft) col else col + eyeSize - 1
            grid[resolvedRow + eyeSize - 1][pupilCol] = PUPIL_COLOR
        }
    }

    return consumed
}

private const val MIN_LIMB_LENGTH = 2
private const val MAX_LIMB_LENGTH = 5

/**
 * Choose up to pairsNeeded columns from the left-half candidates, evenly spaced, skipping any
 * column that would land a limb right next to an already chosen one (or its mirror on the other
 * side) -- limbs always keep at least a 1 pixel gap between them.
 */
private fun selectLimbColumns(
    half: List<Int>,
    width: Int,
    pairsNeeded: Int,
): List<Int> {
    if (half.isEmpty() || pairsNeeded <= 0) return emptyList()

    fun conflicts(
        col: Int,
        chosen: List<Int>,
    ): Boolean {
        val mirrorCol = width - 1 - col
        if (mirrorCol != col && abs(mirrorCol - col) <= 1) return true
        return chosen.any { c -> abs(col - c) <= 1 || abs(col - (width - 1 - c)) <= 1 }
    }

    val step = maxOf(1, half.size / pairsNeeded)
    val chosen = mutableListOf<Int>()
    var i = 0
    while (i < half.size && chosen.size < pairsNeeded) {
        val col = half[i]
        if (!conflicts(col, chosen)) chosen.add(col)
        i += step
    }

    if (chosen.size < pairsNeeded) {
        for (col in half) {
            if (chosen.size >= pairsNeeded) break
            if (col in chosen) continue
            if (!conflicts(col, chosen)) chosen.add(col)
        }
    }

    return chosen
}

private fun paintLimb(
    grid: Array<Array<String>>,
    col: Int,
    edge: Int,
    length: Int,
    color: String,
    growDown: Boolean,
    height: Int,
) {
    for (depth in 1..length) {
        val row = if (growDown) edge + depth else edge - depth
        if (row in 0 until height) grid[row][col] = color
    }
}

/**
 * Paint up to `count` limbs from chosenCols. A limb and its mirror are always added together (or,
 * for a column on the centre line, as a single self-mirrored limb) so the result stays
 * left-right symmetric, and a limb is only drawn when there's room for at least MIN_LIMB_LENGTH pixels.
 */
private fun placeLimbs(
    grid: Array<Array<String>>,
    width: Int,
    height: Int,
    edgeByCol: Map<Int, Int>,
    chosenCols: List<Int>,
    count: Int,
    color: String,
    growDown: Boolean,
    random: Random,
) {
    var remaining = count
    for (col in chosenCols) {
        if (remaining <= 0) break
        val mirrorCol = width - 1 - col
        val edge = edgeByCol.getValue(col)
        val available = if (growDown) height - 1 - edge else edge
        val maxLen = minOf(MAX_LIMB_LENGTH, available)
        if (maxLen < MIN_LIMB_LENGTH) continue
        val unit = if (mirrorCol == col) 1 else 2
        if (unit > remaining) continue

        val length = random.nextInt(MIN_LIMB_LENGTH, maxLen + 1)
        paintLimb(grid, col, edge, length, color, growDown, height)
        remaining -= 1
        if (mirrorCol != col) {
            val mirrorEdge = edgeByCol[mirrorCol] ?: edge
            paintLimb(grid, mirrorCol, mirrorEdge, length, color, growDown, height)
            remaining -= 1
        }
    }
}

private fun addLegs(
    grid: Array<Array<String>>,
    mask: Set<Pair<Int, Int>>,
    width: Int,
    height: Int,
    legs: Int,
    color: String,
    random: Random,
) {
    if (legs <= 0 || mask.isEmpty()) return
    val bodyBottomByCol = mutableMapOf<Int, Int>()
    for ((row, col) in mask) bodyBottomByCol[col] = maxOf(bodyBottomByCol.getOrDefault(col, row), row)
    val candidateCols = bodyBottomByCol.keys.sorted()
    if (candidateCols.isEmpty()) return

    val cx = (width - 1) / 2.0
    var half = candidateCols.filter { it <= cx }
    if (half.isEmpty()) half = candidateCols.take(maxOf(1, candidateCols.size / 2))

    val pairsNeeded = (legs + 1) / 2
    val chosen = selectLimbColumns(half, width, pairsNeeded)
    placeLimbs(grid, width, height, bodyBottomByCol, chosen, legs, color, growDown = true, random)
}

private fun addArms(
    grid: Array<Array<String>>,
    mask: Set<Pair<Int, Int>>,
    width: Int,
    height: Int,
    arms: Int,
    color: String,
    random: Random,
) {
    if (arms <= 0 || mask.isEmpty()) return
    val bodyTopByCol = mutableMapOf<Int, Int>()
    for ((row, col) in mask) bodyTopByCol[col] = minOf(bodyTopByCol.getOrDefault(col, row), row)
    val candidateCols = bodyTopByCol.keys.sorted()
    if (candidateCols.isEmpty()) return

    val cx = (width - 1) / 2.0
    var half = candidateCols.filter { it <= cx }
    if (half.isEmpty()) half = candidateCols.take(maxOf(1, candidateCols.size / 2))

    val pairsNeeded = (arms + 1) / 2
    val chosen = selectLimbColumns(half, width, pairsNeeded)
    placeLimbs(grid, width, height, bodyTopByCol, chosen, arms, color, growDown = false, random)
}

/**
 * Generate an alien as a grid (list of rows) of hex colour strings. `palette` is the name of a
 * built-in palette. Set `border = false` to let the body fill the full width and top row of the
 * grid -- useful for small displays where the default margin would otherwise waste a large
 * fraction of the pixels.
 */
fun generateAlien(
    width: Int = 16,
    height: Int = 16,
    background: String = "#ffffff",
    palette: String = "cga",
    eyes: Int = 2,
    bigEyes: Boolean = false,
    legs: Int? = null,
    arms: Int = 0,
    shape: String? = null,
    border: Boolean = true,
    random: Random = Random.Default,
): List<List<String>> {
    val resolvedLegs = legs ?: random.nextInt(2, 6)
    val resolvedShape = shape ?: SHAPES[random.nextInt(SHAPES.size)]

    val colors = buildPalette(palette, background, random)
    val grid = Array(height) { Array(width) { background } }

    val mask = symmetricMask(width, height, resolvedShape, border, random)
    val bodyColor = colors[random.nextInt(colors.size)]
    for ((row, col) in mask) grid[row][col] = bodyColor

    val consumed = placeEyes(grid, mask, width, eyes, bigEyes, resolvedShape, random)
    val featureMask = mask - consumed

    addLegs(grid, featureMask, width, height, resolvedLegs, bodyColor, random)
    addArms(grid, featureMask, width, height, arms, bodyColor, random)

    return grid.map { it.toList() }
}
