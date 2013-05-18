
import select
import socket
import time

from cPickle import loads

from tiddlyweb.model.tiddler import Tiddler

from parastore import MAX_SERVERS

SOCKFILE = './parastore.sock'
MAX_RETRIES = 5
SLEEP_INT = 0.005

def do_process(tiddlers):
    print 'start', time.time()
    if not tiddlers:
        return
    outputs = []
    inputs = []

    max_index = len(tiddlers)
    write_index = 0
    read_index = 0

    tiddler_data = {}

    def add_socket():
        attempts = 0
        while attempts < MAX_RETRIES:
            try:
                client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                client.connect(SOCKFILE)
                client.setblocking(0)
                outputs.append(client)
                inputs.append(client)
                break
            except socket.error, exc:
                if exc.errno != 61:
                    raise
                else:
                    #print 'doing retry'
                    attempts += 1
                    time.sleep(SLEEP_INT)
        else:
            print 'conn retry attempt failure'

    for x in range(MAX_SERVERS):
        add_socket()

    while True:
        if read_index >= max_index:
            break

        readable, writable, exceptional = select.select(
                inputs, outputs, [])

        for element in writable:
            if write_index < max_index:
                try:
                    tiddler = tiddlers[write_index]
                    element.sendall('%s:%s' % (tiddler.bag, tiddler.title))
                    write_index += 1
                    try:
                        element.shutdown(socket.SHUT_WR)
                    except socket.error, exc:
                        if exc.errno != 57:
                            raise
                    outputs.remove(element)
                    if not outputs and write_index < max_index:
                        add_socket()
                except IndexError:
                    print 'we got confused on tiddler index', element, write_index
                    break
            else:
                outputs.remove(element)

        for element in readable:
            element_done = handle_read(element, tiddler_data)

            if element_done:
                tiddler = loads(tiddler_data[element])
                yield tiddler
                del tiddler_data[element]
                try:
                    element.shutdown(socket.SHUT_RDWR)
                except socket.error, exc:
                    pass
                try:
                    element.close()
                except socket.error, exc:
                    print 'error closing socket', exc
                inputs.remove(element)
                read_index += 1
    print 'finish', time.time()




def handle_read(element, tiddler_data):
    """
    Read a piece of available data on socket element. If the
    socket tells us we have all the data return True.
    """
    element_done = False
    try:
        data = element.recv(1024)
        if element in tiddler_data:
            tiddler_data[element] += data
        else:
            tiddler_data[element] = data
        if len(data) < 1024:
            element_done = True
    except socket.error, exc:
        if exc.errno != 35:
            raise
    return element_done


if __name__ == '__main__':
    x = do_process([
        Tiddler('title 1', 'testbag'),
        Tiddler('title 2', 'testbag'),
        Tiddler('title 3', 'testbag'),
        Tiddler('title 4', 'testbag'),
        Tiddler('title 5', 'testbag'),
        Tiddler('title 100', 'testbag'),
        Tiddler('title 200', 'testbag'),
        Tiddler('title 300', 'testbag'),
        Tiddler('title 400', 'testbag'),
        Tiddler('title 500', 'testbag'),
        Tiddler('title 101', 'testbag'),
        Tiddler('title 202', 'testbag'),
        Tiddler('title 303', 'testbag'),
        Tiddler('title 404', 'testbag'),
        Tiddler('title 505', 'testbag'),
        Tiddler('title 111', 'testbag'),
        Tiddler('title 212', 'testbag'),
        Tiddler('title 313', 'testbag'),
        Tiddler('title 414', 'testbag'),
        Tiddler('title 515', 'testbag'),
        Tiddler('title 10', 'testbag'),
        Tiddler('title 20', 'testbag'),
        Tiddler('title 30', 'testbag'),
        Tiddler('title 40', 'testbag'),
        Tiddler('title 50', 'testbag'),
        Tiddler('title 11', 'testbag'),
        Tiddler('title 21', 'testbag'),
        Tiddler('title 31', 'testbag'),
        Tiddler('title 41', 'testbag'),
        Tiddler('title 51', 'testbag'),
        Tiddler('title 21', 'testbag'),
        Tiddler('title 22', 'testbag'),
        Tiddler('title 32', 'testbag'),
        Tiddler('title 42', 'testbag'),
        Tiddler('title 52', 'testbag'),
        Tiddler('title 6', 'testbag')])

    for thing in x:
        print thing.title, 'in', thing.bag
