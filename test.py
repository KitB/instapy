import instapy
import watcher
import time
import test_funcs

if __name__ == "__main__":
    r = instapy.Reloader(test_funcs.test_rot13)
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
