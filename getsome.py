import cProfile

from tiddlyweb.config import config

from tiddlywebplugins.utils import get_store
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.collections import Tiddlers


def do_stuff():
    store = get_store(config)
    bag = store.get(Bag('testbag'))

    tiddlers = Tiddlers(title='collection')
    tiddlers.bag = bag.name
    tiddlers.store = store

    for tiddler in store.list_bag_tiddlers(bag):
        tiddlers.add(tiddler)

    for tiddler in tiddlers:
        print tiddler.title, len(tiddler.text)


if __name__ == '__main__':
    cProfile.run('do_stuff()', 'profiledata')
