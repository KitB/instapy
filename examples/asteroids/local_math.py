import random
import math


def r(n):
    return int(round(n))


def rand(n):
    return random.uniform(0, n)


def bind_angle(angle):
    return ((angle + math.pi) % (2 * math.pi)) - math.pi
