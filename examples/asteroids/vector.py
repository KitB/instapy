import math

import local_math as lm


def vec_sub(vec_a, vec_b):
    return [a - b for (a, b) in zip(vec_a, vec_b)]


def vec_add(vec_a, vec_b):
    return [a + b for (a, b) in zip(vec_a, vec_b)]


def vec_mod(vec_a, vec_b):
    return [a % b for (a, b) in zip(vec_a, vec_b)]


def vec_scale(vec, scale):
    return [scale * a for a in vec]


def vec_distance((x1, y1), (x2, y2)):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def vec_angle((x1, y1), (x2, y2)):
    (dx, dy) = vec_sub((x1, y1), (x2, y2))
    return lm.bind_angle(math.atan2(dy, dx) - (math.pi / 2))


def vec_mean(vecs):
    ax = 0
    ay = 0
    for x, y in vecs:
        ax += x
        ay += y
    ax /= len(vecs)
    ay /= len(vecs)
    return (ax, ay)


def rotate(points, angle, about):
    c = math.cos(angle)
    s = math.sin(angle)

    def rotate_point(point):
        x, y = vec_sub(point, about)
        xnew = (x * c) - (y * s)
        ynew = (x * s) + (y * c)
        return vec_add((xnew, ynew), about)

    return map(rotate_point, points)


def all_round_points(points):
    def _r(point):
        return map(lm.r, point)
    return map(_r, points)
