package com.simongarton.alien.ui

import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import com.simongarton.alien.generator.PALETTE_NAMES
import com.simongarton.alien.generator.generateAlien
import kotlin.random.Random

const val BACKGROUND_HEX = "#000000"
val BACKGROUND_COLOR = Color.Black
const val MAX_ALIENS_ON_SCREEN = 5

private const val MIN_GRID_SIZE = 8
private const val MAX_GRID_SIZE = 24
private const val MIN_CELL_PX = 4f
private const val MAX_RENDER_FRACTION_OF_HALF_SCREEN = 1f
private const val MIN_RENDER_FRACTION_OF_HALF_SCREEN = 0.3f
private const val MIN_FADE_MS = 1200
private const val MAX_FADE_MS = 2400
private const val MIN_HOLD_MS = 4000
private const val MAX_HOLD_MS = 9000

data class AlienSprite(
    val id: Long,
    val gridWidth: Int,
    val gridHeight: Int,
    val colors: List<List<Color>>,
    val cellSizePx: Float,
    val start: Offset,
    val end: Offset,
    val fadeInMs: Int,
    val holdMs: Int,
    val fadeOutMs: Int,
)

fun String.toComposeColor(): Color {
    val r = substring(1, 3).toInt(16)
    val g = substring(3, 5).toInt(16)
    val b = substring(5, 7).toInt(16)
    return Color(red = r, green = g, blue = b)
}

/**
 * Build a randomly-shaped, randomly-sized alien, magnified to a random fraction of half the
 * screen's smaller dimension, positioned at a random start/end point it will drift between
 * while fully on screen.
 */
fun createAlienSprite(
    id: Long,
    screenWidthPx: Float,
    screenHeightPx: Float,
    random: Random = Random,
): AlienSprite {
    val gridWidth = random.nextInt(MIN_GRID_SIZE, MAX_GRID_SIZE + 1)
    val gridHeight = random.nextInt(MIN_GRID_SIZE, MAX_GRID_SIZE + 1)
    val palette = PALETTE_NAMES[random.nextInt(PALETTE_NAMES.size)]

    val hexGrid =
        generateAlien(
            width = gridWidth,
            height = gridHeight,
            background = BACKGROUND_HEX,
            palette = palette,
            eyes = if (random.nextBoolean()) 2 else 3,
            bigEyes = random.nextBoolean(),
            legs = random.nextInt(2, 6),
            arms = random.nextInt(0, 4),
            shape = null,
            random = random,
        )
    val colors = hexGrid.map { row -> row.map { it.toComposeColor() } }

    // Magnify up to half the screen's smaller dimension, varying the fraction so aliens aren't
    // all the same size.
    val minScreenDim = minOf(screenWidthPx, screenHeightPx)
    val maxRenderDim = minScreenDim * 0.5f
    val fraction =
        MIN_RENDER_FRACTION_OF_HALF_SCREEN +
            random.nextFloat() * (MAX_RENDER_FRACTION_OF_HALF_SCREEN - MIN_RENDER_FRACTION_OF_HALF_SCREEN)
    val targetDim = maxRenderDim * fraction
    val gridMaxDim = maxOf(gridWidth, gridHeight)
    val cellSizePx = maxOf(MIN_CELL_PX, targetDim / gridMaxDim)

    val renderWidth = gridWidth * cellSizePx
    val renderHeight = gridHeight * cellSizePx

    fun randomPosition(): Offset {
        val x = if (screenWidthPx > renderWidth) random.nextFloat() * (screenWidthPx - renderWidth) else 0f
        val y = if (screenHeightPx > renderHeight) random.nextFloat() * (screenHeightPx - renderHeight) else 0f
        return Offset(x, y)
    }

    return AlienSprite(
        id = id,
        gridWidth = gridWidth,
        gridHeight = gridHeight,
        colors = colors,
        cellSizePx = cellSizePx,
        start = randomPosition(),
        end = randomPosition(),
        fadeInMs = random.nextInt(MIN_FADE_MS, MAX_FADE_MS + 1),
        holdMs = random.nextInt(MIN_HOLD_MS, MAX_HOLD_MS + 1),
        fadeOutMs = random.nextInt(MIN_FADE_MS, MAX_FADE_MS + 1),
    )
}
