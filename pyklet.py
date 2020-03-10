import inspect
class Pyklet:
    def __init__(self, *args, **kwargs):
        self._source = inspect.getsource(self.__class__)
        self._hashObjects = (args, kwargs, self._source)
