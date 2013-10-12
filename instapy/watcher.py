import time

from watchdog import events
from watchdog import observers
from instapy import reloader


class Notifier(events.FileSystemEventHandler):
    def __init__(self, reloader):
        super(Notifier, self).__init__()
        self.reloader = reloader

    def on_modified(self, event):
        self.reloader.update()


def run_with_file_watcher(looper):
    r = reloader.Reloader(looper)
    handler = Notifier(r)
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
