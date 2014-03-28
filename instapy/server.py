import SimpleXMLRPCServer as sxmls
import threading
import xmlrpclib

import logging

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 16180


class Server(threading.Thread):
    def __init__(self, reloader, host=DEFAULT_HOST, port=DEFAULT_PORT,
                 *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)

        self.reloader = reloader
        self.address = (host, port)

        self.server = sxmls.SimpleXMLRPCServer((host, port),
                                               allow_none=True)
        self.server.register_function(self.reloader.update, 'update')
        self.server.register_function(self.reloader.restart, 'restart')
        self.server.register_function(self.reloader.pause, 'pause')
        self.server.register_function(self.reloader.unpause, 'unpause')
        self.server.register_function(self.reloader.toggle_pause,
                                      'toggle_pause')

        self.daemon = True
        self.name = "Server Thread"

    def run(self):
        logging.debug('Listening to %s on port %d' % self.address)
        self.server.serve_forever()


def get_reloader_proxy(address="http://%s:%d" % (DEFAULT_HOST, DEFAULT_PORT),
                       *args, **kwargs):
    """ To be used in clients, gives them a proxy object to use """
    return xmlrpclib.ServerProxy(address, *args, allow_none=True, **kwargs)
