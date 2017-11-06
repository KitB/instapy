# stdlib
import math
import time
import random
import logging  # noqa

# external packages
import pygame

# local modules
import local_math as lm
import vector as v
import values


def make_surface(dims):
    s = pygame.surface.Surface(dims)
    s.set_colorkey(values.colorkey)
    s.fill(values.colorkey)
    return s


class Physical(object):
    def __init__(self, (x, y), (vx, vy), radius, angle):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.angle = angle
        self.radius = radius
        self.to_delete = False

    @property
    def position(self):
        return self.x, self.y

    @position.setter
    def position(self, (x, y)):
        self.x, self.y = x, y

    @property
    def int_position(self):
        return lm.r(self.x), lm.r(self.y)

    @property
    def velocity(self):
        return self.vx, self.vy

    @velocity.setter
    def velocity(self, (vx, vy)):
        self.vx, self.vy = vx, vy

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, angle):
        self._angle = lm.bind_angle(angle)

    def rotate(self, angle):
        self.angle = self.angle + angle

    def _make_drawable(self):
        radius = lm.r(self.radius)
        side = radius * 2
        self._drawable = make_surface((side, side))
        pygame.draw.circle(self._drawable, values.white,
                           (radius, radius), radius)
        pygame.draw.circle(self._drawable, values.black,
                           (radius, radius), radius - 2)
        pygame.draw.line(self._drawable, values.white,
                         (radius, radius), (radius, 0))

    @property
    def drawable(self):
        try:
            return self._drawable
        except AttributeError:
            self._make_drawable()
            return self._drawable

    def __instapy_update__(self, old, new):
        del self._drawable

    def draw(self, screen):
        s = pygame.transform.rotate(self.drawable, -math.degrees(self.angle))
        w, h = s.get_size()
        x, y = self.int_position
        x = x - (w / 2)
        y = y - (h / 2)
        screen.blit(s, (x, y))

    def update(self, dt_ratio):
        pos = v.vec_add(self.position, v.vec_scale(self.velocity,
                                                   dt_ratio))
        self.position = v.vec_mod(pos, (640, 640))

    def is_colliding(self, other_physical):
        return (v.vec_distance(self.position, other_physical.position)
                <= self.radius + other_physical.radius)

    def __eq__(self, o):
        return ((self.x, self.y, self.vx, self.vy, self.radius, self.angle)
                == (o.x, o.y, o.vx, o.vy, o.radius, o.angle))


class Player(Physical):
    def __init__(self, (x, y)):
        super(Player, self).__init__((x, y), (0, 0), 7, 0)
        self.shape = (7, 10, 10)

    def _make_drawable(self):
        self._drawable = make_surface((32, 44))
        (x, y) = 16, 22
        (d_side, d_back, d_front) = self.shape
        points = [(x - d_side, y - d_back),
                  (x, y + d_front),
                  (x + d_side, y - d_back)]
        points = v.all_round_points(points)
        pygame.draw.polygon(self._drawable, values.white, points, 3)

    def add_velocity(self, dt_ratio, sub=False):
        additional_velocity = v.rotate([(0, 20)], self.angle, (0, 0))[0]
        scale = -dt_ratio if sub else dt_ratio
        additional_velocity = v.vec_scale(additional_velocity, scale)
        self.velocity = v.vec_add(self.velocity, additional_velocity)


class Asteroid(Physical):
    def __init__(self, (x, y), (vx, vy), radius, angle):
        super(Asteroid, self).__init__((x, y), (vx, vy), radius, angle)

    def split(self):
        if self.radius > 5:
            a1 = Asteroid(self.position, (lm.rand(10), lm.rand(10)),
                          self.radius / 2, lm.rand(math.pi * 2))
            a2 = Asteroid(self.position, (lm.rand(10), lm.rand(10)),
                          self.radius / 2, lm.rand(math.pi * 2))
            return [a1, a2]
        else:
            return []

    def score(self):
        return 20.0 / self.radius

    @classmethod
    def generate(cls):
        return cls((lm.rand(640), lm.rand(640)),
                   (lm.rand(10), lm.rand(10)),
                   lm.r(lm.rand(40) + 20), lm.rand(math.pi * 2))

    def _make_drawable(self):
        radius = self.radius
        self._drawable = make_surface((radius * 4, radius * 4))
        x, y = 2 * radius, 2 * radius
        distance_angles = [(random.gauss(radius, radius / 6), i * (math.pi / 4))
                           for i in xrange(8)]
        point_differences = [(d * math.cos(a), d * math.sin(a))
                             for (d, a) in distance_angles]
        points = [(x + dx, y + dy)
                  for (dx, dy) in point_differences]
        pygame.draw.polygon(self._drawable, values.white, points, 2)


class Bullet(Physical):
    def __init__(self, (x, y), (vx, vy), angle):
        super(Bullet, self).__init__((x, y), (vx, vy), 5, angle)

    def _make_drawable(self):
        self._drawable = make_surface((3, 12))
        pygame.draw.line(self._drawable, values.white, (2, 1), (2, 5))


class LaserBeam(Physical):
    def __init__(self, (x, y), angle):
        super(LaserBeam, self).__init__((x, y), (0, 0), 1, angle)

    def _make_drawable(self):
        self._drawable = make_surface((23, 2000))
        pygame.draw.line(self._drawable, (127 * (math.sin(time.time()) + 1), 127 * (math.cos(time.time()) + 1), 0),
                         (10, 1000), (10, 1998), 20)

    def is_colliding(self, other):
        a = v.vec_angle(self.position, other.position) - self.angle
        if abs(a) < math.pi / 2:
            return False
        o = abs(math.sin(a) * v.vec_distance(self.position, other.position))
        return o < other.radius + 20


class Explosion(Physical):
    def __init__(self, (x, y), starting_radius=5, max_radius=60):
        super(Explosion, self).__init__((x, y), (0, 0), starting_radius, 0)
        self.max_radius = max_radius

    def update(self, dt_ratio):
        super(Explosion, self).update(dt_ratio)
        self.radius += 200 * dt_ratio
        if self.radius > self.max_radius:
            self.to_delete = True
        try:
            del self._drawable
        except AttributeError:
            pass

    def _make_drawable(self):
        side = lm.r(self.radius * 2)
        self._drawable = make_surface((side, side))
        pygame.draw.circle(self._drawable, values.white,
                           (lm.r(self.radius), lm.r(self.radius)),
                           lm.r(self.radius))
        try:
            pygame.draw.circle(self._drawable, values.black,
                               (lm.r(self.radius), lm.r(self.radius)),
                               lm.r(self.radius - 10))
        except ValueError:
            pass
