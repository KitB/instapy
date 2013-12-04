import logging

from watchdog import events
from watchdog import observers


def begin_auto_update(reloader):
    """ Spawns a thread that will automatically perform the update on save.

        Returns:
            The handler object in use e.g. to pass into the GUI
    """
    handler = Handler(reloader)
    observer = observers.Observer()
    observer.schedule(handler, path='.', recursive=True)
    observer.start()
    return handler


class Handler(events.FileSystemEventHandler):
    def __init__(self, reloader):
        super(Handler, self).__init__()
        self.reloader = reloader
        self.paused = False

    def on_modified(self, event):
        if not self.paused:
            logging.debug('Performing update')
            self.reloader.update()
        else:
            logging.debug('File modification detected but paused so no update.')
