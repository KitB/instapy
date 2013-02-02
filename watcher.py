import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Notifier(FileSystemEventHandler):
    def __init__(self, reloader):
        super(Notifier, self).__init__()
        self.reloader = reloader

    def on_modified(self, event):
        self.reloader.update()


if __name__ == "__main__":
    event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()
