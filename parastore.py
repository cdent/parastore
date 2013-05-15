
import os
import SocketServer

from tiddlyweb.config import config
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import StoreError
from tiddlywebplugins.utils import get_store

SOCKFILE = './parastore.sock'
STORE = get_store(config)


class StoreSocketHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        print 'i am process', os.getpid()
        data = self.rfile.readline().strip()
        if data:
            print 'GOT DATA', data
            bag_name, tiddler_title = data.split(':', 1) #  change to \x00
            bag_name = bag_name.decode('utf-8')
            tiddler_title = tiddler_title.decode('utf-8')
            tiddler = Tiddler(tiddler_title, bag_name)
            try:
                tiddler = STORE.get(tiddler)
                self.wfile.write(tiddler.text)
            except StoreError:
                self.wfile.write('\x00ERROR')
        else:
            print 'DIDNT'


class ProcessSocketServer(SocketServer.ForkingMixIn,
        SocketServer.UnixStreamServer):

    #allow_reuse_address = True
    request_queue_size = 5
    timeout = 30


def cleanup():
    if os.path.exists(SOCKFILE):
        os.unlink(SOCKFILE)


def start_server():
    server = ProcessSocketServer(SOCKFILE, StoreSocketHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == '__main__':
    cleanup()
    print 'starting server'
    start_server()
