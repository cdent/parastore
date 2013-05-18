
import os
import sys
import socket
from select import select

from tiddlyweb.config import config
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import StoreError
from tiddlywebplugins.utils import get_store

MAX_SERVERS = 5
SOCKFILE = './parastore.sock'
STORE = get_store(config)

def handle(conn):
    content = ''
    while True:
        data = conn.recv(1024)
        if data:
            content += data
            if len(data) < 1024:
                break
        else:
            break
    if content:
        print 'GOT DATA', content, 'in', os.getpid()
        bag_name, tiddler_title = content.split(':', 1) #  change to \x00
        bag_name = bag_name.decode('utf-8')
        tiddler_title = tiddler_title.decode('utf-8')
        tiddler = Tiddler(tiddler_title, bag_name)
        try:
            tiddler = STORE.get(tiddler)
            conn.sendall(tiddler.text)
        except StoreError, exc:
            print 'got store error', exc
            conn.sendall('\x00ERROR')
    else:
        print 'got no content', os.getpid()
    conn.close()


def start_single_server(server):
    try:
        while True:
            conn, addr = server.accept()
            handle(conn)
    except KeyboardInterrupt:
        sys.exit(0)


def cleanup():
    if os.path.exists(SOCKFILE):
        os.unlink(SOCKFILE)


def start_servers(count):
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKFILE)
    server.listen(5)
    children = []
    for child in range(count):
        pid = os.fork()
        if pid:
            children.append(pid)
        else:
            start_single_server(server)

    # in master
    while children:
        try:
            pid, status = os.waitpid(-1, 0)
            print 'child %s died with %s' % (pid, status)
            children.remove(pid)
        except KeyboardInterrupt:
            sys.exit(0)


if __name__ == '__main__':
    cleanup()
    print 'starting servers'
    start_servers(MAX_SERVERS)
