#!/usr/bin/env python
import time

from instapy import watcher, server


def main():
    proxy = server.get_reloader_proxy('http://localhost:16180')
    handler = watcher.begin_auto_update(proxy)

    while True:
        time.sleep(0.1)


if __name__ == '__main__':
    main()
