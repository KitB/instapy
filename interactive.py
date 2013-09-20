# File: interactive.py
# Allows the user to control the ball
import pygame
import pygame.gfxdraw
from pygame.locals import *
import instapy


class Game(instapy.Looper):
    def __init__(self, *args, **kwargs):
        self.done = False

    def init_once(self):
        pygame.init()
        self.dims = (640, 400)
        self.screen = pygame.display.set_mode(self.dims)
        self.clock = pygame.time.Clock()

    def init(self):
        self.black = (0, 0, 0)
        self.purple = (116, 4, 181)
        self.ball_pos = (120, 120)
        self.ball_velocity = (800, -400)
        self.gravity = 900
        self.jump = 900
        self.move = 900
        self.friction = 0.8
        self.elasticity = 0.7
        self.radius = 40
        self.stick = False

    def update_ball(self):
        dt = self.clock.tick(60)
        dt_seconds = dt / 1000.0
        self.ball_pos = [a + (b * dt_seconds) for (a, b) in zip(self.ball_pos, self.ball_velocity)]
        self.ball_velocity = [n * (1 - (self.friction * dt_seconds)) for n in self.ball_velocity]
        self.ball_velocity[1] += self.gravity * dt_seconds
        left = top = self.radius
        right = self.dims[0] - self.radius
        bottom = self.dims[1] - self.radius
        if self.ball_pos[1] <= top:
            self.ball_pos[1] = top
            if not self.stick and self.ball_velocity[1] < 0:
                self.ball_velocity[1] *= -self.elasticity
            elif self.stick:
                self.ball_velocity[1] = 0
        elif self.ball_pos[1] >= bottom:
            self.ball_pos[1] = bottom
            if not self.stick and self.ball_velocity[1] > 0:
                self.ball_velocity[1] *= -self.elasticity
            elif self.stick:
                self.ball_velocity[1] = 0

        if self.ball_pos[0] <= left:
            self.ball_pos[0] = left
            if not self.stick and self.ball_velocity[0] < 0:
                self.ball_velocity[0] *= -self.elasticity
            elif self.stick:
                self.ball_velocity[0] = 0
        elif self.ball_pos[0] >= right:
            self.ball_pos[0] = right
            if not self.stick and self.ball_velocity[0] > 0:
                self.ball_velocity[0] *= -self.elasticity
            elif self.stick:
                self.ball_velocity[0] = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[K_w]:
                    self.ball_velocity[1] -= self.jump
                if keys[K_s]:
                    self.ball_velocity[1] += self.jump
                if keys[K_a]:
                    self.ball_velocity[0] -= self.move
                if keys[K_d]:
                    self.ball_velocity[0] += self.move
                if keys[K_SPACE]:
                    self.stick = True
                if keys[K_q]:
                    self.done = True
            elif event.type == KEYUP:
                keys = pygame.key.get_pressed()
                if not keys[K_SPACE]:
                    self.stick = False

    def loop_body(self):
        self.handle_events()
        self.update_ball()
        self.screen.fill(self.black)
        draw(self.screen, self.ball_pos, self.purple, self.radius)
        pygame.display.flip()
        return self.done


def darken((R, G, B)):
    """ Make a colour a little darker """
    return (R / 4, G / 4, B / 4)


def draw(screen, ball_pos, purple, radius):
    pos = [int(round(n)) for n in ball_pos]
    pygame.gfxdraw.filled_circle(screen, pos[0], pos[1], radius, purple)
    pygame.gfxdraw.filled_circle(screen, pos[0], pos[1], radius - 5, darken(purple))
