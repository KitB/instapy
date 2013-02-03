import instapy
import watcher
import time

import ball


if __name__ == "__main__":
    r = instapy.Reloader(ball.do_frame, ball.init, ball.init_once)
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
