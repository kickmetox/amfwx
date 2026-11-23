"""Chroma key and compositing helpers."""

from __future__ import annotations

from pathlib import Path


def _distance(pixel, key):
    return sum((int(pixel[index]) - int(key[index])) ** 2
               for index in range(3)) ** 0.5


def chroma_key(image, key=(0, 255, 0), tolerance=60, softness=20,
               spill=0.5):
    """Return RGBA image with the key color removed."""
    image = image.convert("RGBA")
    width, height = image.size
    source = image.load()
    output = image.copy()
    target = output.load()
    tolerance = float(tolerance)
    softness = max(1.0, float(softness))
    for y in range(height):
        for x in range(width):
            r, g, b, _a = source[x, y]
            distance = _distance((r, g, b), key)
            if distance <= tolerance:
                alpha = 0
            elif distance >= tolerance + softness:
                alpha = 255
            else:
                alpha = int(255 * (distance - tolerance) / softness)
            if alpha < 255 and spill:
                # reduce the dominant key channel towards the other two
                red, green, blue = r, g, b
                if key[1] >= key[0] and key[1] >= key[2]:
                    green = min(green, int(max(red, blue) + 255 * spill))
                target[x, y] = (red, green, blue, alpha)
            else:
                target[x, y] = (r, g, b, alpha)
    return output


def composite(foreground, background, position=(0, 0)):
    foreground = foreground.convert("RGBA")
    background = background.convert("RGBA")
    canvas = background.copy()
    canvas.alpha_composite(foreground, dest=position)
    return canvas


def save_chroma(image, path, key=(0, 255, 0), tolerance=60, softness=20,
                spill=0.5):
    result = chroma_key(image, key, tolerance, softness, spill)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    result.save(path)
    return str(path)
