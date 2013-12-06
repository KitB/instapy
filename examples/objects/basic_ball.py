import pygame
from instapy import reloader


class Colour(pygame.Color):
    def __init__(self, r, g, b):
        super(Colour, self).__init__(r, g, 0, 255)

    def darken(self):
        return Colour(self.r / 10, self.g / 10, self.b / 10)

black = Colour(0, 0, 0)
white = Colour(255, 255, 255)


class Ball(object):
    def __init__(self, pos, colour, radius, velocity):
        self.pos = pos
        self.colour = colour
        self.radius = radius
        self.velocity = velocity

    def update(self, dt_seconds):
        self.pos = [a + (b * dt_seconds)
                    for (a, b) in zip(self.pos, self.velocity)]

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
        pygame.draw.circle(screen, self.colour, pos, self.radius)
        pygame.draw.circle(screen, self.colour.darken(),
                           pos, self.radius - 5)

    def vertical_bounce(self):
        self.velocity[1] = -self.velocity[1]
        if abs(self.velocity[1]) < 60:
            self.velocity[1] = 0

    def horizontal_bounce(self):
        self.velocity[0] = -self.velocity[0]
        if abs(self.velocity[0]) < 60:
            self.velocity[0] = 0


class Game(reloader.Looper):
    def init_once(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 640))
        self.clock = pygame.time.Clock()

    def init(self):
        self.bg = black
        radius = 25
        self.ball = Ball((160, radius), white, 25, [800, 400])

    def loop_body(self):
        self.update_ball()
        self.draw()

    def draw(self):
        # Redraw the background
        self.screen.fill(self.bg)

        self.ball.draw(self.screen)

        # Switch to the new buffer in video memory
        pygame.display.flip()

    def update_ball(self):
        dt = self.clock.tick(60)
        dt_seconds = dt / 1000.0

        self.ball.update(dt_seconds)
