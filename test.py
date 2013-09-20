import instapy
import watcher
from watchdog import observers
import time

import interactive


if __name__ == "__main__":
    r = instapy.LooperReloader(interactive.Game())
    handler = watcher.Notifier(r)
    o = observers.Observer()
    o.schedule(handler, path='.', recursive=True)
    o.start()
    r.start()
    try:
        while True:
            if not r.is_alive():
                o.stop()
                o.join()
                break
            time.sleep(1)
    except KeyboardInterrupt:
        pass
