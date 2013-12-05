import pygame
from instapy import reloader


black = (0, 0, 0)
white = (255, 255, 255)
purple = (128, 0, 128)


class Ball(object):
    def __init__(self, pos, colour, radius, velocity):
        self.pos = pos
        self.colour = colour
        self.radius = radius
        self.velocity = velocity


class Game(reloader.Looper):
    def init_once(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 640))
        self.clock = pygame.time.Clock()

    def init(self):
        self.bg = black

        radius = 25
        self.ball = Ball((160, radius), purple, 25, [800, 400])

        self.elasticity = 1.0

    def loop_body(self):
        self.update_ball()
        self.draw()

    def draw(self):
        # Redraw the background
        self.screen.fill(self.bg)

        # Draw the foreground
        ## First we need drawable coordinates because we want subpixel precision
        ## when calculating but we can only draw in integer pixel coordinates
        pos = [int(round(n)) for n in self.ball.pos]
        pygame.draw.circle(self.screen, self.ball.colour, pos, self.ball.radius)
        pygame.draw.circle(self.screen, darken(self.ball.colour),
                           pos, self.ball.radius - 5)

        # Switch to the new buffer in video memory
        pygame.display.flip()

    def update_ball(self):
        dt = self.clock.tick(60)
        dt_seconds = dt / 1000.0

        # I know these lines are ridiculous but I like them anyway
        self.ball.pos = [a + (b * dt_seconds)
                         for (a, b) in zip(self.ball.pos, self.ball.velocity)]

        if self.ball.pos[1] > 640 - self.ball.radius:
            self.ball.pos[1] = 640 - self.ball.radius
            self.vertical_bounce()
        elif self.ball.pos[1] < self.ball.radius:
            self.ball.pos[1] = self.ball.radius
            self.vertical_bounce()

        if self.ball.pos[0] > 640 - self.ball.radius:
            self.ball.pos[0] = 640 - self.ball.radius
            self.horizontal_bounce()
        elif self.ball.pos[0] < self.ball.radius:
            self.ball.pos[0] = self.ball.radius
            self.horizontal_bounce()

    def vertical_bounce(self):
            self.ball.velocity[1] = self.ball.velocity[1] * -self.elasticity
            if abs(self.ball.velocity[1]) < 60:
                self.ball.velocity[1] = 0

    def horizontal_bounce(self):
            self.ball.velocity[0] = self.ball.velocity[0] * -self.elasticity
            if abs(self.ball.velocity[0]) < 60:
                self.ball.velocity[0] = 0


def darken((r, g, b)):
    """ Make a darker version of a colour """
    return (r / 4, g / 4, b / 4)
