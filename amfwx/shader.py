"""Tiny software vertex/fragment shader pipeline for AMFWX."""

from __future__ import annotations

import math

from .canvas import Color
from .render3d import transform


class Shader:
    def vertex(self, position, uv, normal=(0, 0, 1)):
        """Return (clip_position, varyings) or None to discard."""
        return position, (uv[0], uv[1])

    def fragment(self, varyings):
        u, v = varyings[0], varyings[1]
        return Color(int(255 * u), int(255 * v), 128)


class ShaderRenderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.zbuffer = [float("inf")] * (width * height)

    def render(self, canvas, vertices, triangles, shader, matrix,
               uvs=None, normals=None):
        self.zbuffer = [float("inf")] * (canvas.width * canvas.height)
        compiled = []
        for index, position in enumerate(vertices):
            uv = uvs[index] if uvs and index < len(uvs) else (0.0, 0.0)
            normal = normals[index] if normals and index < len(normals) else (0, 0, 1)
            result = shader.vertex(position, uv, normal)
            if result is None:
                compiled.append(None)
                continue
            clip, varyings = result
            world = transform(matrix, clip)
            if world[3] <= 0:
                compiled.append(None)
                continue
            x = (world[0] / world[3] + 1) * canvas.width / 2
            y = (1 - world[1] / world[3]) * canvas.height / 2
            compiled.append((x, y, world[2] / world[3], varyings,
                             1.0 / world[3]))
        for triangle in triangles:
            points = [compiled[index] for index in triangle]
            if any(point is None for point in points):
                continue
            self._triangle(canvas, points, shader)
        return canvas

    def _triangle(self, canvas, points, shader):
        a, b, c = points
        min_x = max(0, int(min(a[0], b[0], c[0])))
        max_x = min(canvas.width - 1, int(max(a[0], b[0], c[0])))
        min_y = max(0, int(min(a[1], b[1], c[1])))
        max_y = min(canvas.height - 1, int(max(a[1], b[1], c[1])))
        denominator = ((b[1] - c[1]) * (a[0] - c[0]) +
                       (c[0] - b[0]) * (a[1] - c[1]))
        if abs(denominator) < 1e-9:
            return
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                w0 = ((b[1] - c[1]) * (x - c[0]) +
                      (c[0] - b[0]) * (y - c[1])) / denominator
                w1 = ((c[1] - a[1]) * (x - c[0]) +
                      (a[0] - c[0]) * (y - c[1])) / denominator
                w2 = 1 - w0 - w1
                if w0 < 0 or w1 < 0 or w2 < 0:
                    continue
                depth = w0 * a[2] + w1 * b[2] + w2 * c[2]
                index = y * canvas.width + x
                if depth >= self.zbuffer[index]:
                    continue
                reciprocal = w0 * a[4] + w1 * b[4] + w2 * c[4]
                varyings = []
                for channel in range(len(a[3])):
                    if reciprocal:
                        value = (w0 * a[3][channel] * a[4] +
                                 w1 * b[3][channel] * b[4] +
                                 w2 * c[3][channel] * c[4]) / reciprocal
                    else:
                        value = a[3][channel]
                    varyings.append(value)
                color = shader.fragment(varyings)
                if color is None:
                    continue
                self.zbuffer[index] = depth
                canvas.set_pixel(x, y, color)
