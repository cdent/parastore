
import select
import socket

from tiddlyweb.model.tiddler import Tiddler

SOCKFILE = './parastore.sock'

def do_process(tiddlers):
    outputs = []
    inputs = []

    max_index = len(tiddlers)
    write_index = 0
    read_index = 0

    def add_socket():
        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(SOCKFILE)
            client.setblocking(0)
            outputs.append(client)
            inputs.append(client)
        except socket.error, exc:
            if exc.errno != 61:
                raise
            else:
                print 'got', exc

    add_socket()

    while True:
        if read_index >= max_index:
            break

        readable, writable, exceptional = select.select(
                inputs, outputs, [])

        for element in readable:
            output = ''
            while True:
                try:
                    data = element.recv(1024)
                except socket.error, exc:
                    if exc.errno != 35:
                        raise
                else:
                    if data:
                        output += data
                    else:
                        break

            yield output[:3]
            try:
                element.close()
            except socket.error, exc:
                print 'error closing socket', exc
            inputs.remove(element)
            read_index += 1

        for element in writable:
            if write_index < max_index:
                try:
                    if len(outputs) < 2:
                        add_socket()
                    tiddler = tiddlers[write_index]
                    element.sendall('%s:%s\n' % (tiddler.bag, tiddler.title))
                    write_index += 1
                    element.shutdown(socket.SHUT_WR)
                    outputs.remove(element)
                except IndexError:
                    print 'we got confused on tiddler index', element, write_index
                    break
            else:
                outputs.remove(element)

        for element in exceptional:
            pass


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
        Tiddler('title 10', 'testbag'),
        Tiddler('title 20', 'testbag'),
        Tiddler('title 30', 'testbag'),
        Tiddler('title 40', 'testbag'),
        Tiddler('title 50', 'testbag'),
        Tiddler('title 6', 'testbag')])

    for thing in x:
        print thing
