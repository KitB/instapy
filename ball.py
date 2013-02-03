import pygame


def init_once():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))

    return (screen,)


def init():
    # Some colours
    black = (0, 0, 0)
    purple = (116, 4, 181)

    ball_pos = (400, 120)
    radius = 40

    return (black, purple, ball_pos, radius)


def darken((R, G, B)):
    """ Make a colour a little darker """
    return (R / 4, G / 4, B / 4)


def draw(screen, black, purple, ball_pos, radius):
    pygame.draw.circle(screen, darken(purple), ball_pos, radius)
    pygame.draw.circle(screen, purple, ball_pos, radius, 1)

def do_frame(screen, black, purple, ball_pos, radius):
    screen.fill(black)
    draw(screen, black, purple, ball_pos, radius)
    pygame.display.flip()
