import pygame
from pygame.locals import K_s, K_w, K_a, K_d, KEYDOWN, K_SPACE, MOUSEBUTTONDOWN,\
                          MOUSEBUTTONUP, MOUSEMOTION
from instapy import reloader
from math import sqrt


class Ball(object):
    def __init__(self, x, y, r, game):
        self.pos = (x, y)
        self.old_pos = self.pos
        self.velocity = (0, 0)
        self.radius = r
        self.purple = (255, 255, 255)

        self.game = game

        self.mouse_moving = False
        self.mouse_done = False

    def update(self, dt):
        dt_seconds = dt / 1000.0
        if self.mouse_moving:
            self.old_pos = self.pos
            return
        elif self.mouse_done:
            self.mouse_done = False
            self.velocity = vector_subtract(self.pos, self.old_pos, dt * 3)
            print self.velocity
        self.pos = [a + (b * dt_seconds) for (a, b) in zip(self.pos, self.velocity)]
        self.velocity = [n * (1 - (self.game.damping * dt_seconds)) for n in self.velocity]
        self.velocity[1] += self.game.gravity * dt_seconds

        if self.pos[1] > 640 - self.radius:
            self.pos[1] = 640 - self.radius
            self.vertical_bounce()
        elif self.pos[1] < self.radius:
            self.pos[1] = self.radius
            self.vertical_bounce()

        if self.pos[0] > 640 - self.radius:
            self.pos[0] = 640 - self.radius
            self.horizontal_bounce()
        elif self.pos[0] < self.radius:
            self.pos[0] = self.radius
            self.horizontal_bounce()

    def draw(self, screen):
        pos = [int(round(n)) for n in self.pos]
        pygame.draw.circle(screen, self.purple, pos, self.radius)
        pygame.draw.circle(screen,
                           darken(self.purple),
                           pos,
                           self.radius - 5)

    def vertical_bounce(self):
            self.velocity[1] = self.velocity[1] * -self.game.elasticity
            if abs(self.velocity[1]) < 400:
                self.velocity[1] = 0

    def horizontal_bounce(self):
            self.velocity[0] = self.velocity[0] * -self.game.elasticity


class Game(reloader.Looper):
    def init_once(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 640))
        self.clock = pygame.time.Clock()

    def init(self):
        self.purple = (188, 0, 198)

        self.gravity = 4900
        self.jump = 1900
        self.move = 900
        self.radius = 50
        self.damping = 0.8
        self.elasticity = 0.7

        self.mouse_moving = False
        self.mouse_done = False

        self.ball = Ball(200, 200, 50, self)

    def update_ball(self):
        dt = self.clock.tick(60)
        self.ball.update(dt)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[K_w]:
                    self.ball.velocity[1] -= self.jump
                if keys[K_s]:
                    self.ball.velocity[1] += self.jump
                if keys[K_a]:
                    self.ball.velocity[0] -= self.move
                if keys[K_d]:
                    self.ball.velocity[0] += self.move

                if keys[K_SPACE]:
                    self.gravity = -self.gravity
                    print "inverting"
            elif event.type == MOUSEBUTTONDOWN:
                if vector_distance(event.pos, self.ball.pos) < self.ball.radius:
                    self.mouse_moving = True
            elif event.type == MOUSEBUTTONUP:
                if self.mouse_moving:
                    self.mouse_moving = False
                    self.mouse_done = True
            elif event.type == MOUSEMOTION:
                if self.mouse_moving:
                    self.ball.pos = event.pos

    def loop_body(self):
        self.handle_events()
        self.update_ball()
        self.screen.fill((0, 0, 0))
        self.draw()
        pygame.display.flip()
        self.clock.tick(60)

    def draw(self):
        self.ball.draw(self.screen)


def darken((r, g, b)):
    return (r / 4, g / 4, b / 4)


def vector_distance((x1, y1), (x2, y2)):
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def vector_subtract((x1, y1), (x2, y2), factor=1):
    return ((x1 - x2) * factor, (y1 - y2) * factor)
