import logging

from watchdog import events


# TODO: Unify naming of notifier (it is also known as handler and watcher,
# unacceptable)
class Notifier(events.FileSystemEventHandler):
    def __init__(self, reloader):
        super(Notifier, self).__init__()
        self.reloader = reloader
        self.paused = False

    def on_modified(self, event):
        if not self.paused:
            logging.debug('Performing update')
            self.reloader.update()
        else:
            logging.debug('File modification detected but paused so no update.')
