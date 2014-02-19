from instapy import reloader


class Element(object):
    def __init__(self, game):
        self._game = game


class Game(reloader.Looper):
    def __init_once__(self):
        pass

    def __init__(self):
        self.lst = [Element(self), Element(self)]

    def loop_body(self):
        print [e._game is self for e in self.lst]
