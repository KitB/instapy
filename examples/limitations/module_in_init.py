"""Minimal example used while fixing a bug

Bug was fixed in commit 37135fdae831446835b6b704cfa1e64828dce8e4
so bug was still occurring in commit ba407d2d8ea38a1f699e457f600812f430bc71c6
"""
import math
import time

from instapy import reloader


class Printer(reloader.Looper):
    def init(self):
        self.output = math.pi

    def loop_body(self):
        print self.output
        time.sleep(0.5)
