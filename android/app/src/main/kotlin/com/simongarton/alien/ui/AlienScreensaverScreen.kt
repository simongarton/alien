package com.simongarton.alien.ui

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.key
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.IntOffset
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlin.math.roundToInt
import kotlin.random.Random

private const val MIN_SPAWN_DELAY_MS = 900L
private const val MAX_SPAWN_DELAY_MS = 3000L

@Composable
fun AlienScreensaverScreen(modifier: Modifier = Modifier) {
    BoxWithConstraints(modifier = modifier.fillMaxSize().background(BACKGROUND_COLOR)) {
        val density = LocalDensity.current
        val screenWidthPx = with(density) { maxWidth.toPx() }
        val screenHeightPx = with(density) { maxHeight.toPx() }

        val sprites = remember { mutableStateListOf<AlienSprite>() }
        var nextId by remember { mutableLongStateOf(0L) }

        LaunchedEffect(screenWidthPx, screenHeightPx) {
            if (screenWidthPx <= 0f || screenHeightPx <= 0f) return@LaunchedEffect
            while (true) {
                delay(Random.nextLong(MIN_SPAWN_DELAY_MS, MAX_SPAWN_DELAY_MS))
                if (sprites.size < MAX_ALIENS_ON_SCREEN) {
                    sprites.add(createAlienSprite(id = nextId++, screenWidthPx = screenWidthPx, screenHeightPx = screenHeightPx))
                }
            }
        }

        for (sprite in sprites) {
            key(sprite.id) {
                AnimatedAlien(sprite = sprite, onFinished = { sprites.remove(sprite) })
            }
        }
    }
}

@Composable
private fun AnimatedAlien(
    sprite: AlienSprite,
    onFinished: () -> Unit,
) {
    val alpha = remember { Animatable(0f) }
    val progress = remember { Animatable(0f) }

    LaunchedEffect(sprite.id) {
        val alphaJob =
            launch {
                alpha.animateTo(1f, tween(sprite.fadeInMs))
                delay(sprite.holdMs.toLong())
                alpha.animateTo(0f, tween(sprite.fadeOutMs))
            }
        val progressJob =
            launch {
                progress.animateTo(
                    1f,
                    tween(sprite.fadeInMs + sprite.holdMs + sprite.fadeOutMs, easing = LinearEasing),
                )
            }
        alphaJob.join()
        progressJob.join()
        onFinished()
    }

    val density = LocalDensity.current
    val widthDp = with(density) { (sprite.gridWidth * sprite.cellSizePx).toDp() }
    val heightDp = with(density) { (sprite.gridHeight * sprite.cellSizePx).toDp() }

    Canvas(
        modifier =
            Modifier
                .graphicsLayer { this.alpha = alpha.value }
                .offset {
                    val x = sprite.start.x + (sprite.end.x - sprite.start.x) * progress.value
                    val y = sprite.start.y + (sprite.end.y - sprite.start.y) * progress.value
                    IntOffset(x.roundToInt(), y.roundToInt())
                }.size(widthDp, heightDp),
    ) {
        for (row in sprite.colors.indices) {
            val rowColors = sprite.colors[row]
            for (col in rowColors.indices) {
                val color = rowColors[col]
                if (color == BACKGROUND_COLOR) continue
                drawRect(
                    color = color,
                    topLeft = Offset(col * sprite.cellSizePx, row * sprite.cellSizePx),
                    size = Size(sprite.cellSizePx, sprite.cellSizePx),
                )
            }
        }
    }
}
