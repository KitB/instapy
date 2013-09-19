from watchdog.events import FileSystemEventHandler


class Notifier(FileSystemEventHandler):
    def __init__(self, reloader):
        super(Notifier, self).__init__()
        self.reloader = reloader

    def on_modified(self, event):
        self.reloader.update()
