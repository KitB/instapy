# File: bouncing.py
# Makes the ball bounce off of the edges of the window
import pygame
import instapy
from math import cos, sin
import time


class Game(instapy.Looper):
    def init_once(self):
        pygame.init()
        self.dims = (640, 480)
        self.screen = pygame.display.set_mode(self.dims)
        self.clock = pygame.time.Clock()

    def init(self):
        # Some colours
        self.black = (0, 0, 0)
        self.purple = (116, 4, 181)

        self.ball_pos = (120, 120)
        self.ball_velocity = (800, -400)
        self.gravity = 200
        self.friction = 0.4
        self.elasticity = 0.7
        self.radius = 40

    def update_ball(self):
        dt = self.clock.tick(60)
        dt_seconds = dt / 1000.0
        self.ball_pos = [a + (b * dt_seconds) for (a, b) in zip(self.ball_pos, self.ball_velocity)]
        self.ball_velocity = [n * (1 - (self.friction * dt_seconds)) for n in self.ball_velocity]
        self.ball_velocity[1] += self.gravity * dt_seconds
        if self.ball_pos[1] < self.radius and self.ball_velocity[1] < 0:
            self.ball_velocity[1] *= -self.elasticity
        elif self.ball_pos[1] > (self.dims[1] - self.radius) and self.ball_velocity[1] > 0:
            self.ball_velocity[1] *= -self.elasticity

        if self.ball_pos[0] < self.radius and self.ball_velocity[0] < 0:
            self.ball_velocity[0] *= -self.elasticity
        elif self.ball_pos[0] > (self.dims[0] - self.radius) and self.ball_velocity[0] > 0:
            self.ball_velocity[0] *= -self.elasticity

    def loop_body(self):
        t = time.time()
        purple = ((cos(t) * 128) + 127, (sin(t) * 128) + 127, 255 - ((sin(t) * 128) + 127))
        self.update_ball()
        self.screen.fill(darken(invert(purple)))
        draw(self.screen, self.ball_pos, purple, self.radius)
        pygame.display.flip()

def darken((R, G, B)):
    """ Make a colour a little darker """
    return (R / 4, G / 4, B / 4)


def invert((R, G, B)):
    """ Invert a colour """
    return (255 - R, 255 - G, 255 - B)


def draw(screen, ball_pos, purple, radius):
    pos = [int(round(n)) for n in ball_pos]
    pygame.draw.circle(screen, purple, pos, radius)
    pygame.draw.circle(screen, darken(purple), pos, radius - 5)




