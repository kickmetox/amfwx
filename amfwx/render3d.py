"""Small software 3D renderer for AMFWX (no GPU)."""

from __future__ import annotations

import math

from .canvas import Color


def vec(x, y, z):
    return (float(x), float(y), float(z))


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def mul(a, factor):
    return (a[0] * factor, a[1] * factor, a[2] * factor)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def normalize(value):
    length = math.sqrt(dot(value, value)) or 1.0
    return (value[0] / length, value[1] / length, value[2] / length)


def identity():
    return [[1.0 if row == column else 0.0 for column in range(4)]
            for row in range(4)]


def multiply(a, b):
    return [[sum(a[row][k] * b[k][column] for k in range(4))
             for column in range(4)] for row in range(4)]


def perspective(fov=60.0, aspect=1.0, near=0.1, far=100.0):
    factor = 1.0 / math.tan(math.radians(fov) / 2)
    return [
        [factor / aspect, 0, 0, 0],
        [0, factor, 0, 0],
        [0, 0, (far + near) / (near - far), 2 * far * near / (near - far)],
        [0, 0, -1, 0],
    ]


def look_at(eye, target, up=(0, 1, 0)):
    forward = normalize(sub(target, eye))
    right = normalize(cross(forward, up))
    real_up = cross(right, forward)
    return [
        [right[0], right[1], right[2], -dot(right, eye)],
        [real_up[0], real_up[1], real_up[2], -dot(real_up, eye)],
        [-forward[0], -forward[1], -forward[2], dot(forward, eye)],
        [0, 0, 0, 1],
    ]


def translate(x, y, z):
    matrix = identity()
    matrix[0][3], matrix[1][3], matrix[2][3] = x, y, z
    return matrix


def rotate_y(angle):
    c, s = math.cos(angle), math.sin(angle)
    return [[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]]


def transform(matrix, point):
    x, y, z = point
    return (matrix[0][0] * x + matrix[0][1] * y + matrix[0][2] * z + matrix[0][3],
            matrix[1][0] * x + matrix[1][1] * y + matrix[1][2] * z + matrix[1][3],
            matrix[2][0] * x + matrix[2][1] * y + matrix[2][2] * z + matrix[2][3],
            matrix[3][0] * x + matrix[3][1] * y + matrix[3][2] * z + matrix[3][3])


class Texture:
    def __init__(self, width, height, data=None):
        self.width = max(1, int(width))
        self.height = max(1, int(height))
        self.data = data or bytearray(self.width * self.height * 4)
        self.levels = [(self.width, self.height, self.data)]
        self._build_mips()

    def _build_mips(self):
        width, height, data = self.levels[0]
        while width > 1 or height > 1:
            width = max(1, width // 2)
            height = max(1, height // 2)
            source_width, source_height, source = self.levels[-1]
            target = bytearray(width * height * 4)
            for y in range(height):
                for x in range(width):
                    total = [0, 0, 0, 0]
                    for dy in range(2):
                        for dx in range(2):
                            sx = min(source_width - 1, x * 2 + dx)
                            sy = min(source_height - 1, y * 2 + dy)
                            index = (sy * source_width + sx) * 4
                            for channel in range(4):
                                total[channel] += source[index + channel]
                    index = (y * width + x) * 4
                    for channel in range(4):
                        target[index + channel] = total[channel] // 4
            self.levels.append((width, height, target))

    @classmethod
    def from_canvas(cls, canvas):
        return cls(canvas.width, canvas.height, bytearray(canvas.data))

    @classmethod
    def from_png(cls, path):
        from .canvas import Canvas
        return cls.from_canvas(Canvas.from_png(path))

    def _texel(self, level, x, y):
        width, height, data = self.levels[level]
        x = max(0, min(width - 1, x))
        y = max(0, min(height - 1, y))
        index = (y * width + x) * 4
        b, g, r, a = data[index:index + 4]
        return r, g, b, a or 255

    def sample(self, u, v, lod=0.0):
        level = max(0, min(len(self.levels) - 1, int(round(lod))))
        width, height, _data = self.levels[level]
        x = max(0.0, min(1.0, u)) * (width - 1)
        y = max(0.0, min(1.0, v)) * (height - 1)
        x0, y0 = int(x), int(y)
        x1, y1 = min(width - 1, x0 + 1), min(height - 1, y0 + 1)
        fx, fy = x - x0, y - y0
        c00 = self._texel(level, x0, y0)
        c10 = self._texel(level, x1, y0)
        c01 = self._texel(level, x0, y1)
        c11 = self._texel(level, x1, y1)
        channels = []
        for index in range(4):
            top = c00[index] * (1 - fx) + c10[index] * fx
            bottom = c01[index] * (1 - fx) + c11[index] * fx
            channels.append(int(top * (1 - fy) + bottom * fy))
        return Color(channels[0], channels[1], channels[2], channels[3])


class Camera:
    def __init__(self, eye=(0, 0, 3), target=(0, 0, 0), up=(0, 1, 0),
                 fov=60.0, aspect=1.0, near=0.1, far=100.0):
        self.eye = eye
        self.target = target
        self.up = up
        self.fov = fov
        self.aspect = aspect
        self.near = near
        self.far = far

    def matrix(self):
        return multiply(perspective(self.fov, self.aspect, self.near,
                                    self.far),
                        look_at(self.eye, self.target, self.up))


def clip_near(points, near=0.1):
    """Clip a view-space polygon against z = -near (Sutherland-Hodgman)."""
    result = []
    if not points:
        return result
    previous = points[-1]
    previous_inside = previous[2] <= -near
    for current in points:
        current_inside = current[2] <= -near
        if current_inside != previous_inside:
            t = (-near - previous[2]) / (current[2] - previous[2])
            result.append((previous[0] + t * (current[0] - previous[0]),
                           previous[1] + t * (current[1] - previous[1]),
                           -near))
        if current_inside:
            result.append(current)
        previous = current
        previous_inside = current_inside
    return result


class Mesh:
    def __init__(self, vertices=None, faces=None):
        self.vertices = list(vertices or [])
        self.faces = list(faces or [])

    def add_face(self, indices, color=Color(90, 150, 240), uvs=None):
        self.faces.append((tuple(indices), color, uvs))
        return self


def cube(size=1.0):
    half = size / 2
    vertices = [
        vec(-half, -half, -half), vec(half, -half, -half),
        vec(half, half, -half), vec(-half, half, -half),
        vec(-half, -half, half), vec(half, -half, half),
        vec(half, half, half), vec(-half, half, half),
    ]
    uv = ((0, 0), (1, 0), (1, 1), (0, 1))
    faces = [
        ((0, 1, 2, 3), Color(70, 120, 220), uv),
        ((4, 5, 6, 7), Color(90, 160, 250), uv),
        ((0, 1, 5, 4), Color(60, 110, 200), uv),
        ((2, 3, 7, 6), Color(80, 140, 230), uv),
        ((1, 2, 6, 5), Color(100, 170, 255), uv),
        ((0, 3, 7, 4), Color(50, 100, 190), uv),
    ]
    return Mesh(vertices, faces)


class SoftwareRenderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.zbuffer = [float("inf")] * (width * height)

    def render(self, canvas, mesh, matrix, light=(0.4, 0.8, -0.6), texture=None,
               normal_map=None):
        self.zbuffer = [float("inf")] * (canvas.width * canvas.height)
        projected = []
        for vertex in mesh.vertices:
            clip = transform(matrix, vertex)
            if clip[3] <= 0:
                projected.append(None)
                continue
            nx, ny, nz = clip[0] / clip[3], clip[1] / clip[3], clip[2] / clip[3]
            projected.append(((nx + 1) * canvas.width / 2,
                              (1 - ny) * canvas.height / 2, nz,
                             1.0 / clip[3]))
        for face in mesh.faces:
            indices, color = face[0], face[1]
            uvs = face[2] if len(face) > 2 else None
            points = [projected[index] for index in indices]
            if any(point is None for point in points):
                continue
            normal = normalize(cross(sub(mesh.vertices[indices[1]],
                                         mesh.vertices[indices[0]]),
                                     sub(mesh.vertices[indices[2]],
                                         mesh.vertices[indices[0]])))
            if normal_map is not None and uvs is not None:
                center_u = sum(uv[0] for uv in uvs) / len(uvs)
                center_v = sum(uv[1] for uv in uvs) / len(uvs)
                sample = normal_map.sample(center_u, center_v)
                tangent = normalize(sub(mesh.vertices[indices[1]],
                                        mesh.vertices[indices[0]]))
                bitangent = cross(normal, tangent)
                nx = sample.r / 127.5 - 1.0
                ny = sample.g / 127.5 - 1.0
                normal = normalize(add(normal, add(mul(tangent, nx),
                                                   mul(bitangent, ny))))
            intensity = 0.35 + 0.65 * max(0.0, -dot(normal, normalize(light)))
            shade = Color(int(color.r * intensity), int(color.g * intensity),
                          int(color.b * intensity))
            for index in range(1, len(points) - 1):
                uv_triangle = None
                if uvs is not None:
                    uv_triangle = (uvs[0], uvs[index], uvs[index + 1])
                self._triangle(canvas, points[0], points[index],
                               points[index + 1], shade, texture,
                               uv_triangle)

    def _triangle(self, canvas, a, b, c, color, texture=None, uvs=None):
        min_x = max(0, int(min(a[0], b[0], c[0])))
        max_x = min(canvas.width - 1, int(max(a[0], b[0], c[0])))
        min_y = max(0, int(min(a[1], b[1], c[1])))
        max_y = min(canvas.height - 1, int(max(a[1], b[1], c[1])))
        area = abs((b[0] - a[0]) * (c[1] - a[1]) -
                   (c[0] - a[0]) * (b[1] - a[1])) / 2
        lod = 0.0
        if texture is not None and area > 0:
            lod = max(0.0, math.log2(math.sqrt(area) /
                                     max(1.0, max(texture.width,
                                                   texture.height))))
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
                if depth < self.zbuffer[index]:
                    self.zbuffer[index] = depth
                    final = color
                    if texture is not None and uvs is not None:
                        reciprocal = (w0 * a[3] + w1 * b[3] + w2 * c[3])
                        if reciprocal:
                            u = (w0 * uvs[0][0] * a[3] +
                                 w1 * uvs[1][0] * b[3] +
                                 w2 * uvs[2][0] * c[3]) / reciprocal
                            v = (w0 * uvs[0][1] * a[3] +
                                 w1 * uvs[1][1] * b[3] +
                                 w2 * uvs[2][1] * c[3]) / reciprocal
                        else:
                            u = v = 0.0
                        sample = texture.sample(u, v, lod)
                        final = Color(int(color.r * sample.r / 255),
                                      int(color.g * sample.g / 255),
                                      int(color.b * sample.b / 255))
                    canvas.set_pixel(x, y, final)
