import inspect
import pickle

class Pyklet:
    _TAG_ = '_pyklet_'
    def __init__(self, *args):
        self._source = inspect.getsource(self.__class__)
        self._hashObjects = (args, kwargs, self._source)
        self._pickleClass = pickle.dumps(self.__class__)
        self._args = args
    def __reduce__(self):
        return (self.__class__, self._args)
