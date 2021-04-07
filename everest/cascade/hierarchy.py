###############################################################################
''''''
###############################################################################

from . import _reseed

from functools import lru_cache as _lru_cache
from collections.abc import MutableMapping as _MutableMapping

def flatten_hierarchy(hierarchy):
    return dict(_flatten_hierarchy(hierarchy))
def _flatten_hierarchy(hierarchy):
    for k, v in hierarchy.items():
        if isinstance(v, Hierarchy):
            for sk, sv in _flatten_hierarchy(v):
                yield sk, sv
        else:
            yield k, v

def concatenate_hierarchy(d, parent_key = '', sep = '_'):
    # by Imran@stackoverflow
    items = []
    parent_key = parent_key.strip(sep)
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, _MutableMapping):
            items.extend(concatenate_hierarchy(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

class Item:
    key: str = None
    _value = None
    def __init__(self, key, val, /):
        self.key = key
        self._value = val
    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, newval):
        self._value = newval
    def __str__(self):
        return repr(self.value)
    def __repr__(self):
        return f'{type(self).__name__}({self.key}: {str(self)})'

class Hierarchy(dict):
    parent = None
    subs = None
    hashint = None
    def __init__(self, *args, __parent__ = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = __parent__
        self.subs = dict()
        self.hashint = _reseed.digits()
    def flatten(self) -> dict:
        return flatten_hierarchy(self)
    def concatenate(self) -> dict:
        return concatenate_hierarchy(self)
    def remove_ghosts(self):
        for key, val in list(self.items()):
            if key.startswith('_'):
                del self[key]
            elif isinstance(val, type(self)):
                val.remove_ghosts()
    def sub(self, key) -> 'Hierarchy':
        self.subs[key] = subhier = type(self)(__parent__ = self)
        super().__setitem__(key, subhier)
        return subhier
    def __getitem__(self, arg, /):
        out = self.raw_getitem(arg)
        if isinstance(out, Item):
            return out.value
        return out
    @_lru_cache
    def raw_getitem(self, arg) -> Item:
        if isinstance(arg, tuple):
            out = self
            for subarg in arg:
                out = out.raw_getitem(subarg)
            return out
        try:
            return super().__getitem__(arg)
        except KeyError as exc:
            for sub in self.subs.values():
                try:
                    return sub.raw_getitem(arg)
                except KeyError:
                    pass
            raise KeyError from exc
    def __setitem__(self, key, val):
        try:
            targ = self.raw_getitem(key)
            if isinstance(targ, Item):
                targ.value = val
            else:
                raise ValueError("Cannot manually set hierarchy.")
        except KeyError:
            if isinstance(val, Hierarchy):
                sub = self.sub(key)
                for subkey, subval in val.items():
                    sub[subkey] = subval
            else:
                super().__setitem__(key, Item(key, val))
    def __hash__(self):
        return self.hashint
    def __repr__(self):
        return type(self).__name__ + super().__repr__()
    def _repr_pretty_(self, p, cycle):
        typnm = type(self).__name__
        if cycle:
            p.text(typnm + '{...}')
        else:
            with p.group(4, typnm + '({', '})'):
                for idx, (key, val) in enumerate(self.items()):
                    if isinstance(val, Item):
                        val = val.value
                    if idx:
                        p.text(',')
                    p.breakable()
                    p.pretty(key)
                    p.text(': ')
                    p.pretty(val)
                p.breakable()
    def copy(self):
        out = type(self)()
        for key, val in self.items():
            out[key] = val
        return out
###############################################################################
###############################################################################
