import time
import rot13


def test_rot13():
    s = "you.just.lost.the.game"
    r = "antidisestablishmentarianism"
    print rot13.main(s)
    time.sleep(5)
