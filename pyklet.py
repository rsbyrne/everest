import inspect
import pickle

# from .builts import Built, Meta # <- causes circular reference
# from .globevars import _BUILTTAG_, _CLASSTAG_

from .exceptions import NotYetImplemented

class Pyklet:
    _TAG_ = '_pyklet_'
    def __init__(self, *args, **kwargs):
        self._source = inspect.getsource(self.__class__)
        args = [
            self._process_input(arg)
            for arg in args
            ]
        kwargs = {
            self._process_input(k): self._process_input(v)
                for k, v in sorted(kwargs.items())
            }
        self._hashObjects = (args, kwargs, self._source)
        self._pickleClass = pickle.dumps(self.__class__)
        self._args, self._kwargs = args, kwargs
    def __reduce__(self):
        return (self._unpickle, (self._args, self._kwargs))
    @classmethod
    def _unpickle(cls, args, kwargs):
        return cls(*args, **kwargs)
    @staticmethod
    def _process_input(inp):
        return inp
    # def _process_input(inp):
    #     if type(inp) is Meta:
    #         raise NotYetImplemented
    #         # return _CLASSTAG_ + inp.script
    #     elif isinstance(inp, Built):
    #         raise NotYetImplemented
    #         # return _BUILTTAG_ + inp.hashID
    #     else:
    #         return inp
    @staticmethod
    def _unprocess_input(inp):
        return inp
