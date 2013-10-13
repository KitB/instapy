import math

import pygame
import pygame.draw
import pygame.event
from pygame.locals import KEYDOWN, KEYUP, K_a, K_d

from instapy import reloader


def r(n):
    return int(round(n))


def vec_sub(vec_a, vec_b):
    return [a - b for (a, b) in zip(vec_a, vec_b)]


def vec_add(vec_a, vec_b):
    return [a + b for (a, b) in zip(vec_a, vec_b)]


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
        return map(r, point)
    return map(_r, points)


class Game(reloader.Looper):
    def init_once(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 640))
        self.clock = pygame.time.Clock()

    def init(self):
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.radius = 40

        self.angle = 1.0
        self.x, self.y = 320, 320

        self.shape = (7, 10, 10)

        self.turn_speed = 3.14159

        self.velocity = (0, 0)

    def draw(self):
        self.screen.fill(self.black)

        (x, y) = self.x, self.y
        (d_side, d_back, d_front) = self.shape
        points = [(x - d_side, y - d_back),
                  (x, y + d_front),
                  (x + d_side, y - d_back)]
        points = rotate(points, self.angle, (x, y))
        points = all_round_points(points)
        pygame.draw.polygon(self.screen, self.white, points, 3)

        pygame.display.flip()

    def update_scene(self):
        (self.x, self.y) = vec_add((self.x, self.y), self.velocity)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                pass
            elif event.type == KEYUP:
                pass
        keys = pygame.key.get_pressed()
        if keys[K_a]:
            self.angle -= self.turn_speed * self.dt_ratio
        if keys[K_d]:
            self.angle += self.turn_speed * self.dt_ratio

    def loop_body(self):
        self.dt_ratio = 1.0 / self.clock.tick(60)
        self.handle_events()
        self.update_scene()
        self.draw()
