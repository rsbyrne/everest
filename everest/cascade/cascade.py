###############################################################################
''''''
###############################################################################

from . import _wordhash

from .hierarchy import Hierarchy as _Hierarchy

class Cascade(_Hierarchy):
    _hashdepth = 2
    def is_attribute(self, key):
        return key in dir(type(self))
    def __getattr__(self, key):
        if self.is_attribute(key):
            return super().__getattribute__(key)
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError from exc
    def __setattr__(self, key, val):
        if self.is_attribute(key):
            super().__setattr__(key, val)
        else:
            self[key] = val
    def __delattr__(self, key):
        if self.is_attribute(key):
            super().__delattr__(key)
        else:
            del self[key]
    def get_hashID(self):
        tohash = []
        for key, val in self.items():
            if type(val) is type(self):
                val = val.get_hashID()
            tohash.append((key, val))
        tohash = str(tohash)
        hashID = _wordhash.get_random_english(
            self._hashdepth,
            seed = tohash,
            )
        return hashID
    @property
    def hashID(self):
        return self.get_hashID()

###############################################################################
###############################################################################
