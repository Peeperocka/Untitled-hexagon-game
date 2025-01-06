import collections
import math


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_coords(self):
        return self.x, self.y


class Hex:
    def __init__(self, q, r, s):
        if round(q + r + s) != 0:  # сумма векторов должна быть равна 0
            raise ValueError("q + r + s must be 0")

        self.q = q
        self.r = r
        self.s = s

    def __add__(self, other):
        return Hex(self.q + other.q, self.r + other.r, self.s + other.s)

    def __sub__(self, other):
        return Hex(self.q - other.q, self.r - other.r, self.s - other.s)

    def __mul__(self, k):
        return Hex(self.q * k, self.r * k, self.s * k)

    def length(self):
        return (abs(self.q) + abs(self.r) + abs(self.s)) // 2

    def distance(self, other):
        return (self - other).length()

    def round(self):
        qi = int(round(self.q))
        ri = int(round(self.r))
        si = int(round(self.s))
        q_diff = abs(qi - self.q)
        r_diff = abs(ri - self.r)
        s_diff = abs(si - self.s)

        if q_diff > r_diff and q_diff > s_diff:
            qi = -ri - si

        elif r_diff > s_diff:
            ri = -qi - si

        else:
            si = -qi - ri

        return Hex(qi, ri, si)

    def lerp(self, other, t):
        return Hex(self.q * (1.0 - t) + other.q * t,
                   self.r * (1.0 - t) + other.r * t,
                   self.s * (1.0 - t) + other.s * t)

    def linedraw(self, other):
        N = self.distance(other)
        a_nudge = Hex(self.q + 1e-06, self.r + 1e-06, self.s - 2e-06)
        b_nudge = Hex(other.q + 1e-06, other.r + 1e-06, other.s - 2e-06)
        results = []
        step = 1.0 / max(N, 1)
        for i in range(0, N + 1):
            results.append(self.lerp(b_nudge, step * i).round())
        return results

    def to_pixel(self, layout):
        M = layout.orientation
        size = layout.size
        origin = layout.origin
        x = (M.f0 * self.q + M.f1 * self.r) * size.x
        y = (M.f2 * self.q + M.f3 * self.r) * size.y
        return Point(x + origin.x, y + origin.y)


Orientation = collections.namedtuple(
    "Orientation",
    ["f0", "f1", "f2", "f3", "b0", "b1", "b2", "b3", "start_angle"]
)

Layout = collections.namedtuple(
    "Layout",
    ["orientation", "size", "origin"]
)

layout_pointy = Orientation(
    math.sqrt(3.0),
    math.sqrt(3.0) / 2.0, 0.0, 3.0 / 2.0,
    math.sqrt(3.0) / 3.0, -1.0 / 3.0, 0.0,
    2.0 / 3.0, 0.5
)

hex_directions = [
    Hex(1, 0, -1), Hex(1, -1, 0),
    Hex(0, -1, 1), Hex(-1, 0, 1),
    Hex(-1, 1, 0), Hex(0, 1, -1)
]


def hex_direction(direction):
    return hex_directions[direction]


def hex_neighbor(hex, direction):
    return hex + hex_direction(direction)


def hex_diagonal_neighbor(hex, direction):
    hex_diagonals = [Hex(2, -1, -1), Hex(1, -2, 1), Hex(-1, -1, 2), Hex(-2, 1, 1), Hex(-1, 2, -1), Hex(1, 1, -2)]
    return hex + hex_diagonals[direction]


def pixel_to_hex(layout, p):
    M = layout.orientation
    size = layout.size
    origin = layout.origin
    pt = Point((p.x - origin.x) / size.x, (p.y - origin.y) / size.y)
    q = M.b0 * pt.x + M.b1 * pt.y
    r = M.b2 * pt.x + M.b3 * pt.y
    return Hex(q, r, -q - r)


def hex_corner_offset(layout, corner):
    M = layout.orientation
    size = layout.size
    angle = 2.0 * math.pi * (M.start_angle - corner) / 6.0
    return Point(size.x * math.cos(angle), size.y * math.sin(angle))


def polygon_corners(layout, h):
    corners = []
    center = h.to_pixel(layout)
    for i in range(0, 6):
        offset = hex_corner_offset(layout, i)
        corners.append(Point(center.x + offset.x, center.y + offset.y))
    return corners
