###############################################################################
''''''
###############################################################################

import string as _string
import inspect as _inspect
from collections.abc import MutableMapping as _MutableMapping

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

def get_paramlevels(func):

    plainchars = _string.ascii_lowercase + _string.digits + '_,=:/* '
    sourcelines = get_sourcelines(func)

    sig = _inspect.signature(func)
    params = sig.parameters

    assert params
    keys = iter(params)
    key = next(keys)
    mode = None
    paramslist = list()
    indentslist = list()

    for lineno, line in enumerate(sourcelines):

        charno = 0
        for charno, char in enumerate(line):
            if char != ' ':
                break
        assert charno % 4 == 0, (charno, line)
        indentslist.append(charno // 4)
        line = line.lstrip(' ')

        if line[0] == '#':
            line = line.lstrip('#').strip(' ')
            paramslist.append(line)
            continue
        lineparams = list()
        paramslist.append(lineparams)

        clean = ''
        for char in line:
            if mode == '#':
                mode = None
                break
            special = False if char in plainchars else char
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

class Hierarchy(dict):
    parent = None
    def __init__(self, *args, __parent__ = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = __parent__
    def flatten(self):
        return flatten_hierarchy(self)
    def concatenate(self):
        return concatenate_hierarchy(self)
    def remove_ghosts(self):
        for key, val in list(self.items()):
            if key.startswith('_'):
                del self[key]
            elif isinstance(val, type(self)):
                val.remove_ghosts()
    def sub(self, key):
        self[key] = subhier = type(self)(__parent__ = self)
        return subhier

def get_hierarchy(func):
    hierarchy = Hierarchy()
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
    return hierarchy

###############################################################################
###############################################################################
