from instapy import reloader
import time


class Element(object):
    def __init__(self, game):
        self._game = game


class Game(reloader.Looper):
    def __init_once__(self):
        pass

    def __init__(self):
        self.lst = [Element(self), Element(self)]
        self.pair = [20, 21]

    def loop_body(self):
        print [e._game is self for e in self.lst]
        print self.pair
        time.sleep(1)
