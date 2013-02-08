import instapy
import watcher
import time

import bouncing


if __name__ == "__main__":
    r = instapy.LooperReloader(bouncing.Game())
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
