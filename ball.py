import pygame

from math import cos, sin, tan, fmod
import time


def init_once():
    pygame.init()
    screen = pygame.display.set_mode((640, 640))
    clock = pygame.time.Clock()

    return (screen, clock)

bg = [255, 0, 0]

def init():
    global ball_pos
    # Some colours
    black = (0, 0, 0)
    purple = (255, 50, 80)

    yellow = (0, 0, 0)

    ball_pos = (100, 100)
    radius = 100

    return (black, purple, yellow, ball_pos, radius)


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

def do_frame(screen, clock, black, purple, yellow, ball_pos, radius):
    t = time.time() * 1.5
    black = ((sin(t) * 28) + 127, 255 - ((sin(t) * 28) + 127), (cos(t) * 28) + 127)
    purple = ((cos(t) * 128) + 127, (sin(t) * 128) + 127, 255 - ((sin(t) * 128) + 127))

    (x, y) = ball_pos
    x = (sin(t) * 320) + 320
    y = (cos(t) * 40) + 240

    p1 = make_pos((x, y))
    p2 = make_pos((640 - x, 480 - y))
    p3 = make_pos((640 - y, 480 - x))
    p4 = make_pos((y, x))

    screen.fill(black)
    draw(screen, black, purple, p1, rad(p1, radius))
    draw(screen, black, invert(purple), p2, rad(p2, radius))
    #draw(screen, black, invert(purple), p3, rad(p3, radius) / 2)
    #draw(screen, black, invert(purple), p4, rad(p4, radius) / 2)

    pygame.display.flip()
    clock.tick(60)
