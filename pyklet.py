import inspect
import pickle
from collections import OrderedDict
from collections.abc import Mapping, Sequence

from .utilities import w_hash

class Pyklet:
    _TAG_ = '_pyklet_'
    def __init__(self, *args, **kwargs):
        # self._source = inspect.getsource(self.__class__)
        if hasattr(self, '_pickle'):
            args, kwargs = self._pickle()
        self._pickleArgs, self._pickleKwargs = args, kwargs
        self._pickleObjs = tuple([
            *self._pickleArgs,
            *[i for sl in sorted(self._pickleKwargs.items()) for i in sl],
            ])
        self._anchorManager = Meta._anchorManager
    def __reduce__(self):
        # self._pickleClass = pickle.dumps(self.__class__)
        return (self._unpickle, (self._pickleArgs, self._pickleKwargs))
    @classmethod
    def _unpickle(cls, args, kwargs):
        return cls(*args, **kwargs)
    @property
    def contentHash(self):
        if hasattr(self, '_hashID'):
            return self._hashID()
        if hasattr(self, '_hashObjects'):
            return w_hash(self._hashObjects)
        else:
            return w_hash(self._pickleObjs)
    @property
    def hashID(self):
        selfname = type(self).__name__.strip('_')
        return 'Everest' + selfname + '{' + self.contentHash + '}'
    def anchor(self, name, path):
        return self._anchorManager(name, path)
    def touch(self, name = None, path = None):
        conds = [o is None for o in (name, path)]
        if any(conds) and not all(conds):
            raise ValueError
        if not any(conds):
            with self.anchor(name, path) as anchor:
                self._touch()
        else:
            self._touch()
    def _touch(self):
        man = self._anchorManager.get_active()
        man.globalwriter.add_dict(
            {self._TAG_: {self.hashID: pickle.dumps(self)}}
            )
        # search_and_touch(self._pickleObjs)

    def __repr__(self):
        return self.hashID
    def copy(self):
        return type(self)(*self._pickleArgs, **self._pickleKwargs)

def search_and_touch(arg):
    if hasattr(arg, 'touch'):
        arg.touch()
    elif isinstance(arg, Sequence):
        for sub in arg:
            search_and_touch(arg)
    elif isinstance(arg, Mapping):
        for key, sub in sorted({**arg}.items()):
            search_and_touch(sub)

from .builts import Meta, Built
