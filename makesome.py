
import os
from random import random

from tiddlyweb.config import config
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler

from tiddlywebplugins.utils import get_store


def do_stuff():
    store = get_store(config)

    store.put(Bag('testbag'))
    for i in range(1000):
        tiddler = Tiddler('title %s' % i, 'testbag')
        tiddler.text = '%s' % i + 'fadaf\n' * int(random() * 500)
        store.put(tiddler)


def clean_stuff():
    """
    Wipe out the existing store.
    """
    if os.path.exists('test.db'):
        os.unlink('test.db')

if __name__ == '__main__':
    clean_stuff()
    do_stuff()
