###############################################################################
''''''
###############################################################################


import abc as _abc
import collections as _collections
from collections import abc as _collabc
import itertools as _itertools
import functools as _functools
import types as _types
import inspect as _inspect

from everest.utilities import (
    TypeMap as _TypeMap, MultiTypeMap as _MultiTypeMap
    )
from everest.utilities import caching as _caching
from everest.utilities import caching as _caching, classtools as _classtools


def not_none(a, b):
    return b if a is None else a


overprint = _functools.partial(_itertools.starmap, not_none)


def passfn(arg, /):
    return arg


class NotNone(_abc.ABC):

    @classmethod
    def __subclasshook__(cls, other, /):
        return not issubclass(other, type(None))


class Null(_abc.ABC):

    @classmethod
    def __subclasshook__(cls, other, /):
        return False


class Chora(_classtools.ClassInit):
    '''
    The Chora is Everest's abstract master representation
    of the concept of space.
    '''

    __slots__ = ()

    PREFIXES = ('trivial', 'incise', 'retrieve')

    def getitem_tuple(self, incisor: tuple, /, **passfuncs):
        '''Captures the special behaviour implied by `self[a,b]`'''
        length = len(incisor)
        if length == 0:
            return self.trivial(**passfuncs)
        arg0, *argn = incisor
        out = self.__getitem__(arg0, **passfuncs)
        if argn:
            raise NotImplementedError
        return out

    def _trivial_ellipsis_(self, incisor: type(Ellipsis) = Ellipsis, /):
        '''Captures the special behaviour implied by `self[...]`.'''
        return self

    def _retrieve_contains_(self, incisor: Null, /) -> type(None):
        '''Returns the element if this chora contains it.'''
        raise KeyError(f"Element {incisor} not in {repr(self)}.")

    @classmethod
    def _get_chora_rawmeths(cls, /):
        out = dict()
        for attr in cls.__dict__:
            for prefix in cls.PREFIXES:
                if attr.startswith(f"_{prefix}_"):
                    out[attr] = getattr(cls, attr)
                    break
        return out

    @classmethod
    def _pass_through(cls, arg, /):
        return arg

    @classmethod
    def _add_overmethods(cls, /):
        for prefix in cls.PREFIXES:
            if not hasattr(cls, prefix):
                setattr(cls, prefix, cls._pass_through)

    @classmethod
    def _get_defkws(cls, tovals=None, /):
        prefixes = cls.PREFIXES
        if tovals is None:
            tovals = (f"cls.{prefix}" for prefix in prefixes)
        return ', '.join(map(
            '='.join,
            zip(prefixes, tovals)
            ))

    @classmethod
    def _wrap_chora_meth(cls, methname, name, meth, /):

        prefix = name.split('_')[0]
        defkws = cls._get_defkws()
        params = tuple(_inspect.signature(meth).parameters.values())[1:]
        argstrn = ', '.join(
            param.name for param in params if param.kind.value == 0
            )

        exec('\n'.join((
            f"@_functools.wraps(meth)",
            f"def {name}(self, {argstrn}, /, *, {defkws}):",
            f"    return {prefix}(self.{methname}({argstrn}))",
            )))

        wrapper = eval(name)
        wrapper.raw = meth

        return wrapper

    @classmethod
    def _get_chora_wrappedmeths(cls, /):
        chorarawmeths = cls._get_chora_rawmeths()
        return {
            (name := methname.strip('_')):
                cls._wrap_chora_meth(methname, name, meth)
            for methname, meth in chorarawmeths.items()
            }

    @classmethod
    def _get_chora_meths(cls, /):
        out = dict()
        for prefix in ('getitem', *cls.PREFIXES):
            for name in cls.__dict__:
                if name.startswith(prefix + '_'):
                    out[name] = getattr(cls, name)
        return out

    @classmethod
    def _yield_getmeths(cls, /):
        for meth in cls.chorameths.values():
            if 'incisor' in meth.__annotations__:
                yield meth.__annotations__['incisor'], meth

    @classmethod
    def _get_getmeths(cls, /):
        return _TypeMap(cls._yield_getmeths())

    @classmethod
    def _get_getitem(cls, /):
        defkws = cls._get_defkws()
        passkws = cls._get_defkws(cls.PREFIXES)
        exec('\n'.join((
            f"def __getitem__(self, arg, /, {defkws}):",
            f"    try:",
            f"        meth = self.getmeths[type(arg)]",
            f"    except KeyError as exc:",
            f"        raise TypeError('Query type unrecognised.') from exc",
            f"    return meth(self, arg, {passkws})",
            )))
        return eval('__getitem__')

    @classmethod
    def _set_getitem(cls, /):
        meth = cls._get_getitem()
        setattr(cls, '__getitem__', meth)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls._add_overmethods()
        chorameths = cls._get_chora_wrappedmeths()
        for name, meth in chorameths.items():
            setattr(cls, name, meth)
        cls.chorameths = cls._get_chora_meths()
        cls.getmeths = cls._get_getmeths()
        cls.primetype = cls._retrieve_contains_.__annotations__['return']
        cls._set_getitem()

    def __getitem__(self, arg, /):
        '''Placeholder for dynamically generated __getitem__.'''
        raise TypeError

    def __contains__(self, arg, /):
        if isinstance(arg, self.primetype):
            try:
                val = self._retrieve_contains_(arg)
                return True
            except KeyError:
                return False

#     def new_self(self, *args, cls=None, **kwargs):
#         return (type(self) if cls is None else cls)(
#             *overprint(_itertools.zip_longest(self.args, args)),
#             **(self.kwargs | kwargs),
#             )


class Sliceable(Chora):

    @classmethod
    def _yield_slcmeths(cls, /):
        parnames = ('start', 'stop', 'step')
        for methname, meth in cls.chorameths.items():
            if methname.split('_')[1] == 'slice':
                anno = meth.__annotations__
                if all(map(anno.__contains__, parnames)):
                    hint = tuple(map(anno.__getitem__, parnames))
                    yield hint, meth

    @classmethod
    def _get_slcmeths(cls, /):
        return _MultiTypeMap(cls._yield_slcmeths())

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.slcmeths = cls._get_slcmeths()

    def getitem_slicelike(self, incisor: slice, /, **passfuncs):
        slcargs = (incisor.start, incisor.stop, incisor.step)
        meth = self.slcmeths[tuple(map(type, slcargs))]
        return meth(self, *slcargs, **passfuncs)

    def _trivial_slice_(self,
            start: type(None), stop: type(None), step: type(None), /
            ):
        '''Captures the special behaviour implied by `self[:]`.'''
        return self


class Incisable(_classtools.ClassInit):
    '''
    Incisable objects are said to 'contain space'
    because they own a Chora instance
    and point their __getitem__ and __contains__ methods to it.
    '''

    __slots__ = ()

    Chora = Chora

    @classmethod
    def _chora_passthrough(cls, arg, /):
        return arg

    @classmethod
    def _defer_chora_methods(cls, /):

        chcls = cls.Chora
        defkws = chcls._get_defkws((f"self.{st}" for st in chcls.PREFIXES))

        for prefix in chcls.PREFIXES:
            if not hasattr(cls, prefix):
                setattr(cls, prefix, cls._chora_passthrough)

        exec('\n'.join((
            f"def __getitem__(self, arg, /):",
            f"    return self.chora.__getitem__(arg, {defkws})",
            )))
        cls.__getitem__ = eval('__getitem__')

        for name in chcls.chorameths:
            exec('\n'.join((
                f"@_functools.wraps(chcls.{name})",
                f"def {name}(self, /, *args):",
                f"    return self.chora.{name}(*args, {defkws})",
                )))
            setattr(cls, name, eval(name))

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls._defer_chora_methods()

    def _get_chora_params(self, /, *args, **kwargs):
        return args, kwargs

    def _get_chora(self, /):
        args, kwargs = self._get_chora_params()
        return self.Chora(*args, **kwargs)

    def __init__(self, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chora = self._get_chora()

    def __getitem__(self, arg, /):
        '''Placeholder for dynamically generated __getitem__.'''
        raise TypeError

    def __contains__(self, arg, /):
        return self.chora.__contains__(arg)

    def trivial(self, _, /):
        return self


###############################################################################
###############################################################################
