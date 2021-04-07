###############################################################################
''''''
###############################################################################

import string as _string
import inspect as _inspect

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

def get_hierarchy(func, /, *, typ = _Hierarchy):
    hierarchy = typ()
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

def get_cascade(func):
    return get_hierarchy(func, typ = _Cascade)

# def get_cascade(func):
#     return get_hierarchy(func, typ = _Cascade)

# import weakref as _weakref
# from types import FunctionType as _FunctionType, MethodType as _MethodType
# from itertools import zip_longest as _zip_longest
#
# from .cascade import Cascade as _Cascade
#
# def align_args(atup, btup):
#     return tuple(
#         b if a is None else a
#             for a, b in _zip_longest(atup, btup)
#         )
#
# class Inputs(_Cascade):
#     def __init__(self, source: _FunctionType, /, *args, **kwargs) -> None:
#         if any(isinstance(source, t) for t in (_FunctionType, _MethodType)):
#             self._Inputs_sig = _inspect.signature(source)
#         else:
#             raise TypeError(
#                 f"Inputs source must be FunctionType or Inputs type,"
#                 f" not {type(source)}"
#                 )
#         super().__init__(source, *args, **kwargs)
#         self._Inputs_source_ref = _weakref.ref(source)
#     @property
#     def _Inputs_incomplete(self):
#         return tuple(v.key for v in self.values() if isinstance(v, _Req))
#     def _Inputs_unpack(self):
#         if keys := self._Inputs_incomplete:
#             raise ValueError(f"Missing required inputs: {keys}")
#         sig = self._Inputs_sig
#         params = sig.parameters
#         args = []
#         kwargs = dict()
#         for key, val in self.items():
#             if isinstance(val, _Req):
#                 raise ValueError(
#                     f"Cannot unpack incomplete Cascade: {key}: {val.note}"
#                     )
#             try:
#                 param = params[key]
#                 if param.kind.value:
#                     kwargs[key] = val
#                 else:
#                     args.append(val)
#             except KeyError:
#                 kwargs[key] = val
#         self.__dict__['_Inputs_args'] = args
#         self.__dict__['_Inputs_kwargs'] = kwargs
#     @property
#     def args(self):
#         try:
#             return self.__dict__['_Inputs_args']
#         except KeyError:
#             self._Inputs_unpack()
#             return self.args
#     @property
#     def kwargs(self):
#         try:
#             return self.__dict__['_Inputs_kwargs']
#         except KeyError:
#             self._Inputs_unpack()
#             return self.kwargs
#     def copy(self, *args, **kwargs):
#         return self.__class__(
#             self._Inputs_source_ref(), *align_args(args, self.args),
#             name = self.name, **{**self.kwargs, **kwargs},
#             )

###############################################################################
###############################################################################
