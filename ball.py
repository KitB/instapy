import pygame
import instapy

from math import cos, sin, tan, fmod
import time


class Game(instapy.Looper):
    def init_once(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 640))
        self.clock = pygame.time.Clock()

    def init(self):
        # Some colours
        self.yellow = (0, 0, 0)

        self.ball_pos = (100, 500)
        self.radius = 100

    def loop_body(self):
        t = time.time() * 1.5
        self.black = ((sin(t) * 28) + 127, 255 - ((sin(t) * 28) + 127), (cos(t) * 28) + 127)
        self.purple = ((cos(t) * 128) + 127, (sin(t) * 128) + 127, 255 - ((sin(t) * 128) + 127))

        (x, y) = self.ball_pos
        #x = (sin(t) * 320) + 320
        #y = (cos(t) * 40) + 240
        x = (x + 2) % 640
        self.ball_pos = (x, y)

        p1 = make_pos((x, y))
        p2 = make_pos((640 - x, 480 - y))

        self.screen.fill(self.black)
        draw(self.screen, self.black, self.purple, p1, rad(p1, self.radius))

        pygame.display.flip()
        self.clock.tick(60)

def darken((R, G, B)):
    """ Make a colour a little darker """
    return (R / 4, G / 4, B / 4)

def invert((R, G, B)):
    """ Invert a colour """
    return (255 - R, 255 - G, 255 - B)


def draw(screen, black, purple, ball_pos, radius):
    pygame.draw.circle(screen, purple, ball_pos, radius + 5)
    pygame.draw.circle(screen, darken(purple), ball_pos, radius)

def rad((x, y), radius):
    return abs(int(round((y / 640.0) * radius)))

def make_pos((x, y)):
    return int(round(x)), int(round(y))

if __name__ == "__main__":
    import instapy
    import watcher
    import time

    r = instapy.LooperReloader(Game())
    handler = watcher.Notifier(r)
    o = watcher.Observer()
    o.schedule(handler, path='.', recursive=True)
    o.start()
    r.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
