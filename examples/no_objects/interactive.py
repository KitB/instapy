import pygame
import instapy

# Adding an import!
from pygame.locals import KEYDOWN, K_w, K_s, K_a, K_d


black = (0, 0, 0)
white = (255, 255, 255)
purple = (128, 0, 128)


class Game(instapy.Looper):
    def init_once(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 640))
        self.clock = pygame.time.Clock()

    def init(self):
        self.bg = black
        self.ball_colour = purple

        self.ball_pos = (320, 320)
        self.radius = 50

        self.ball_velocity = (20, 20)
        self.damping = 0.8

        self.gravity = 900

        self.elasticity = 0.7

        # Player control speeds
        ## roughly equal to gravity seems to work nicely
        self.jump = 900
        self.move = 900

    def loop_body(self):
        self.handle_events()
        self.update_ball()
        self.draw()

    def draw(self):
        # Redraw the background
        self.screen.fill(self.bg)

        # Draw the foreground
        ## First we need drawable coordinates because we want subpixel precision
        ## when calculating but we can only draw in integer pixel coordinates
        pos = [int(round(n)) for n in self.ball_pos]
        pygame.draw.circle(self.screen, self.ball_colour, pos, self.radius)
        pygame.draw.circle(self.screen, darken(self.ball_colour),
                           pos, self.radius - 5)

        # Switch to the new buffer in video memory
        pygame.display.flip()

    def update_ball(self):
        dt = self.clock.tick(60)
        dt_seconds = dt / 1000.0

        # I know these lines are ridiculous but I like them anyway
        self.ball_pos = [a + (b * dt_seconds) for (a, b) in zip(self.ball_pos, self.ball_velocity)]
        self.ball_velocity = [n * (1 - (self.damping * dt_seconds)) for n in self.ball_velocity]

        self.ball_velocity[1] += self.gravity * dt_seconds

        if self.ball_pos[1] > 640 - self.radius:
            self.ball_pos[1] = 640 - self.radius
            self.vertical_bounce()
        elif self.ball_pos[1] < self.radius:
            self.ball_pos[1] = self.radius
            self.vertical_bounce()

        if self.ball_pos[0] > 640 - self.radius:
            self.ball_pos[0] = 640 - self.radius
            self.horizontal_bounce()
        elif self.ball_pos[0] < self.radius:
            self.ball_pos[0] = self.radius
            self.horizontal_bounce()

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

    def vertical_bounce(self):
            self.ball_velocity[1] = self.ball_velocity[1] * -self.elasticity
            if abs(self.ball_velocity[1]) < 60:
                self.ball_velocity[1] = 0

    def horizontal_bounce(self):
            self.ball_velocity[0] = self.ball_velocity[0] * -self.elasticity
            if abs(self.ball_velocity[0]) < 60:
                self.ball_velocity[0] = 0


def darken((r, g, b)):
    """ Make a darker version of a colour """
    return (r / 4, g / 4, b / 4)
