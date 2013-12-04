import importlib
import sys

from instapy import gui
from instapy import reloader
from instapy import server
from instapy import watcher


def get_game_instance(game_instance_string):
    (module_name, dot, cls_name) = game_instance_string.rpartition('.')
    # This will probably break on Windows machines.
    module_name = '.'.join(module_name.split('/'))
    module = importlib.import_module(module_name)
    cls = module.__dict__[cls_name]
    return cls()


def gui_main(host=server.DEFAULT_HOST, port=server.DEFAULT_PORT):
    proxy = server.get_reloader_proxy('http://%s:%d' % (host, port))
    handler = watcher.begin_auto_update(proxy)
    gui.main(sys.argv, handler)


def main(game_instance_string):
    game_instance = get_game_instance(game_instance_string)
    run_game(game_instance)


def run_game(game_instance):
    game_reloader = reloader.Reloader(game_instance)

    reloader_server = server.Server(game_reloader)

    game_reloader.start()
    reloader_server.start()

    try:
        game_reloader.join()
    except KeyboardInterrupt:
        game_reloader.running = False
        game_reloader.join()
