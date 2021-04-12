###############################################################################
''''''
###############################################################################

import string as _string
import inspect as _inspect
from itertools import zip_longest as _zip_longest
from functools import (
    cached_property as _cached_property,
    lru_cache as _lru_cache,
    partial as _partial,
    )

from .hierarchy import Hierarchy as _Hierarchy
from .cascade import Cascade as _Cascade

def get_sourcelines(func):
    source = _inspect.getsource(func)
    source = source[:source.index(':\n')]
    lines = source.split('\n')
    line0 = lines[0]
    return [
        line0[line0.index('(')+1:],
        *(line.rstrip() for line in lines[1:]),
        ]

def get_defaults(func):
    params = _inspect.signature(func).parameters
    return {name: p.default for name, p in params.items()}

PLAINCHARS = _string.ascii_lowercase + _string.digits + r'_,=:/\* '

def preprocess_line(line):
    charno = 0
    for charno, char in enumerate(line):
        if char != ' ':
            break
    assert charno % 4 == 0, (charno, line)
    line = line.lstrip(' ')
    return line, charno // 4

def process_line(line, mode):
    clean = ''
    for char in line:
        if mode == '#':
            mode = None
            break
        special = False if char in PLAINCHARS else char
        if mode is None:
            if special:
                mode = special
            else:
                clean += char
        else:
            if special:
                if any((
                        special == ')' and mode == '(',
                        special == ']' and mode == '[',
                        special == '}' and mode == '{',
                        special in ("'", '"') and special == mode,
                        )):
                    mode = None
    return clean, mode

def get_paramlevels(func):

    sourcelines = get_sourcelines(func)

    sig = _inspect.signature(func)
    params = sig.parameters

    assert params
    keys = iter(params)
    key = next(keys)
    mode = None
    paramslist = list()
    indentslist = list()

    for line in sourcelines:

        line, nindents = preprocess_line(line)
        indentslist.append(nindents)

        if line[0] == '#':
            line = line.lstrip('#').strip(' ')
            paramslist.append(line)
            continue

        lineparams = list()
        paramslist.append(lineparams)

        clean, mode = process_line(line, mode)

        for chunk in clean.split(','):
            if key in chunk:
                lineparams.append(params[key])
                try:
                    key = next(keys)
                except StopIteration:
                    break

    indentslist = [
        indent - 2 if indent > 0 else indent
            for indent in indentslist
        ]

    return list(zip(indentslist, paramslist))

def get_hierarchy(func, /, *, root = None, typ = _Hierarchy):
    if root is None:
        if not issubclass(typ, _Hierarchy):
            raise TypeError(typ)
        hierarchy = typ()
    else:
        hierarchy = root
    currentlev = 0
    addto = hierarchy
    for level, content in get_paramlevels(func):
        if isinstance(content, str):
            if level == currentlev:
                addto = addto.sub(content)
                currentlev += 1
            continue
        if level <= currentlev:
            while level < currentlev:
                currentlev -= 1
                addto = addto.parent
            for param in content:
                addto[param.name] = param
        else:
            raise Exception("Level hierarchies not analysable.")
    if root is None:
        return hierarchy

def get_cascade(func):
    return get_hierarchy(func, typ = _Cascade)

# def align_args(atup, btup):
#     return tuple(
#         b if a is None else a
#             for a, b in _zip_longest(atup, btup)
#         )

class Inputs(_Cascade):
    _set_locked = False
    signature = None
    get_hashID = _lru_cache(maxsize = None)(_Cascade.get_hashID)
    bndargs, bndkwargs = (), {}
    def __init__(self, parent):
        if isinstance(parent, Inputs):
            super().__init__(parent = parent)
            self.signature = parent.signature
        else: # not ischild:
            super().__init__()
            self.signature = _inspect.signature(parent)
            get_hierarchy(parent, root = self)
            self.setitem_lock()
    def setitem_lock(self):
        self._set_locked = True
        for sub in self.subs.values():
            sub.setitem_lock()
    def setitem_unlock(self):
        self._set_locked = False
        for sub in self.subs.values():
            sub.setitem_unlock()
    @_lru_cache
    def __getitem__(self, key, /):
        return super().__getitem__(key)
    def __setitem__(self, key, val, /):
        if self._set_locked:
            raise TypeError(
                f"Cannot set item on {type(self)} after initialisation."
                f" {key} = {val}"
                )
        super().__setitem__(key, val)
    @_cached_property
    def bind(self):
        return _partial(Bound, self)
    def copy(self):
        raise TypeError(f"Cannot copy object of type={type(self)}")

class Bound(Inputs):
    args, kwargs, bound = None, None, None
    def __init__(self, parent, *args, **kwargs):
        if isinstance(parent, Bound):
            assert not (args or kwargs)
            super().__init__(parent)
            self.bound = parent.bound
            self.bind = parent.bind
        else:
            if not isinstance(parent, Inputs):
                parent = Inputs(parent)
            super().__init__(parent)
            bound = self.bound = self.signature.bind_partial(*args, **kwargs)
            bound.apply_defaults()
            self.args, self.kwargs = bound.args, bound.kwargs
            self.update(parent)
            self.bind = _partial(parent.bind, *args, **kwargs)
    @_lru_cache
    def __getitem__(self, key, /):
        out = super().__getitem__(key)
        if isinstance(out, _inspect.Parameter):
            if key in (argus := self.bound.arguments):
                return argus[key]
        return out

###############################################################################
###############################################################################
