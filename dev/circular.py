import aliases

from everest.uniplex.plex import GLOBALPLEX as plex

with plex.open_file() as file:
    file.file.require_group('foo')

import gc
gc.collect()

from everest.disk import FILES
print(tuple(FILES))

import objgraph
objgraph.show_backrefs(FILES['/home/morpheus/default.plex'], filename='test.png')