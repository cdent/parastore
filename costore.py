
from tiddlyweb.config import config
from tiddlyweb.model.bag import Bag
from tiddlywebplugins.utils import get_store

store = get_store(config)

def fatten_tiddlers(store, downstream):
    print 'starting to embiggen'
    while True:
        try:
            tiddler = store.get((yield))
            downstream.send(tiddler)
        except GeneratorExit:
            downstream.close()
            return

def enumerate_tiddlers():
    while True:
        tiddler = (yield)
        print 'enum', tiddler.title
        yield tiddler


def what():
    bag = store.get(Bag('testbag'))
    num = enumerate_tiddlers()
    num.next()
    fat = fatten_tiddlers(store, num)
    fat.next() # decorate away
    for tiddler in store.list_bag_tiddlers(bag):
        fat.send(tiddler)
    fat.close()


from tiddlyweb.model.collections import Tiddlers
import os

def fat(tiddler):
    #print 'worker', os.getpid()
    tiddler = store.get(tiddler)
    tiddler.store = None
    return tiddler

import time
# override tiddlers so that add and __iter__ are pooled
# and coroutined (that is, add sends to __iter__, I think)
class PooledTiddlers(Tiddlers):

    def __init__(self, *args, **kwargs):
        self.pool = kwargs['pool']
        del kwargs['pool']
        Tiddlers.__init__(self, *args, **kwargs)

    def add_set(self, tiddlers):
        """
        Take a generator of tiddlers and add them.
        """
        if self.pool:
            print 'using pool'
            print 'starting pool', time.time()
            result = self.pool.imap_unordered(fat, tiddlers)
            for tiddler in result:
                tiddler.store = store
                self.add(tiddler)
            print 'ending pool', time.time()
        else:
            for tiddler in tiddlers:
                self.add(tiddler)


from multiprocessing import Pool
def pooltest():
    pool = Pool(processes=35)
    bag = store.get(Bag('testbag'))
    tiddlers = PooledTiddlers(store=store, pool=pool)
    tiddlers.add_set(store.list_bag_tiddlers(bag))
    for tiddler in tiddlers:
        #print tiddler.title
        print '.',

if __name__ == '__main__':
    #what()
    pooltest()


