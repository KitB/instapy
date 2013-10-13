from instapy import reloader
from instapy import watcher
from watchdog import observers
import time

from examples.no_objects import interactive


if __name__ == "__main__":
    r = reloader.LooperReloader(interactive.Game())
    handler = watcher.Notifier(r)
    o = observers.Observer()
    o.schedule(handler, path='.', recursive=True)
    o.start()
    r.start()
    try:
        while True:
            if not r.is_alive():
                break
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        r.running = False
        o.stop()
        o.join()
        r.join()
