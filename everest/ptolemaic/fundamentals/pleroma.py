import weakref

class Pleroma(type):
    _preclasses = weakref.WeakValueDictionary()
    def __getitem__(cls, arg):
        return cls._preclasses[arg]
    def __setitem__(cls, key, val):
        cls._preclasses[key] = val
