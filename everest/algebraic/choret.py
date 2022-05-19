###############################################################################
''''''
###############################################################################


import functools as _functools
import operator as _operator
from collections import deque as _deque, abc as _collabc
import types as _types
import itertools as _itertools

from everest.utilities import (
    TypeMap as _TypeMap,
    caching as _caching,
    NotNone, Null, NoneType, EllipsisType,
    )
from everest import incision as _incision
from everest.epitaph import Epitaph as _Epitaph

from everest.ptolemaic.ousia import Binding as _Binding
from everest.ptolemaic.compound import Compound as _Compound

from . import query as _query
from .chora import TrivialException


class Choret(_Compound):

    def __get__(cls, obj, objtype=None):
        if obj is None:
            return cls
        return cls(obj)


class ChoretBase(metaclass=Choret):

    bound: object

    __req_slots__ = ('boundowner',)

    def __init__(self, /):
        super().__init__()
        self.boundowner = self.bound.__ptolemaic_class__.owner

    def __call__(self, incisor, /, *, caller):
        return caller.__incise_fail__(caller)(incisor)


def _wrap_trivial(meth, /):
    @_functools.wraps(meth)
    def wrapper(self, _, /, *, caller):
        return caller.__incise_trivial__()
    return wrapper

def _wrap_slyce(meth, /):
    @_functools.wraps(meth)
    def wrapper(self, arg, /, *, caller):
        try:
            result = meth(self, arg)
        except TrivialException:
            return caller.__incise_trivial__()
        except Exception as exc:
            return caller.__incise_fail__(arg, exc)
        return caller.__incise_slyce__(result)
    return wrapper

def _wrap_retrieve(meth, /):
    @_functools.wraps(meth)
    def wrapper(self, arg, /, *, caller):
        try:
            result = meth(self, arg)
        except TrivialException:
            return caller.__incise_trivial__()
        except Exception as exc:
            return caller.__incise_fail__(arg, exc)
        return caller.__incise_retrieve__(result)
    return wrapper

def _wrap_fail(meth, /):
    @_functools.wraps(meth)
    def wrapper(self, arg, /, *, caller):
        try:
            result = meth(self, arg)
        except TrivialException:
            return caller.__incise_trivial__()
        except Exception as exc:
            return caller.__incise_fail__(arg, exc)
        return caller.__incise_fail__(arg, result)
    return wrapper

WRAPMETHS = dict(
    trivial=_wrap_trivial,
    slyce=_wrap_slyce,
    retrieve=_wrap_retrieve,
    fail=_wrap_fail,
    )


class Basic(metaclass=Choret):

    MERGETUPLES = ('PREFIXES', 'CHANNELS', 'MULTICHANNELS')
    PREFIXES = ('handle', 'trivial', 'slyce', 'retrieve', 'catch', 'fail')

    def trivial_ellipsis(self, incisor: EllipsisType, /):
        '''Captures the special behaviour implied by `self[...]`.'''
        pass

    def fail_ultimate(self, incisor: object, /):
        '''The ultimate fallback for unrecognised incision types.'''
        return None

    @classmethod
    def update_getmeth_names(cls, /, preprefix=''):
        prefixes = cls.PREFIXES
        methnames = {prefix: _deque() for prefix in prefixes}
        adjprefixes = tuple(
            preprefix + ('_' if preprefix else '') + prefix + '_'
            for prefix in prefixes
            )
        for name in cls.attributes:
            for prefix, deq in zip(adjprefixes, methnames.values()):
                if name.startswith(prefix):
                    deq.append(name)
        setattr(cls,
            preprefix + 'getmethnames',
            _types.MappingProxyType({
                name: tuple(deq) for name, deq in methnames.items()
                })
           )

    @classmethod
    def process_hint(cls, hint, /):
        if isinstance(hint, str):
            try:
                return _operator.attrgetter(hint)(cls)
            except AttributeError:
                return Null
        if isinstance(hint, tuple):
            return tuple(map(cls.process_hint, hint))
        if isinstance(hint, _Epitaph):
            return cls.process_hint(hint.decode())
        return hint

    @classmethod
    def process_multihint(cls, hint, /):
        return tuple[cls.process_hint(hint)]

    @classmethod
    def _yield_getmeths(cls, /,
            preprefix='', defaultwrap=(lambda x: x),
            hintprocess=None, 
            ):
        if hintprocess is None:
            hintprocess = cls.process_hint
        methnames = getattr(cls, preprefix + 'getmethnames')
        seen = set()
        for prefix, deq in methnames.items():
            if not deq:
                continue
            wrap = WRAPMETHS.get(prefix, defaultwrap)
            for name in deq:
                meth = getattr(cls, name)
                hint = hintprocess(meth.__annotations__.get('incisor', cls))
                if hint not in seen:
                    yield hint, wrap(meth)
                    seen.add(hint)

    @classmethod
    def get_switcher_method(cls, channel, sentinel, switchertype=None):

        if switchertype is None:

            def switcher(self, incisor: sentinel, /, *, caller):
                return getattr(self, f"{channel}getmeths")[
                type(incisor)
                ](self, incisor, caller=caller)

        elif switchertype is tuple:

            def switcher(self, incisor: sentinel, /, *, caller):
                return getattr(self, f"{channel}getmeths")[
                tuple(map(type, incisor))
                ](self, incisor, caller=caller)

        else:
            raise TypeError

        return switcher

    @classmethod
    def _add_channel(cls, channel='', hintprocess=None, switchertype=None):
        if isinstance(channel, tuple):
            channel, sentinel = channel
            switchname = f"handle_{channel}"
            if not hasattr(cls, switchname):
                switcher = cls.get_switcher_method(
                    channel, sentinel, switchertype
                    )
                setattr(cls, switchname, switcher)
        cls.update_getmeth_names(channel)
        setattr(cls, f"{channel}getmeths", _TypeMap(cls._yield_getmeths(
            channel, hintprocess=hintprocess
            )))

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        for channel in cls.CHANNELS:
            cls._add_channel(channel)
        for channel in cls.MULTICHANNELS:
            cls._add_channel(channel, cls.process_multihint, tuple)
        cls._add_channel()

    def __call__(self, incisor, /, *, caller):
        return self.getmeths[type(incisor)](self, incisor, caller=caller)


# class Slyce(Basic, _chora.Chora):

#     chora: _chora.Chora = None

#     @classmethod
#     def __class_call__(cls, bound, chora=None):
#         if chora is None:
#             chora = bound.chora
#         return super().__class_call__(bound, chora)

#     def catch_chora(self, incisor: _chora.Chora, /, *, caller):
#         return self.__ptolemaic_class__(self.bound, incisor)

#     def __incise__(self, incisor, /, *, caller):
#         return super().__incise__(self.chora[incisor], caller=caller)


class Sliceable(Basic):

    MULTICHANNELS = (('slice', slice),)

    def handle_slice(self, incisor: slice, /, *, caller):
        return self.slicegetmeths[
            tuple(map(type, (incisor.start, incisor.stop, incisor.step)))
            ](self, incisor, caller=caller)

    def slice_trivial_none(self, incisor: (NoneType, NoneType, NoneType)):
        '''Captures the special behaviour implied by `self[:]`.'''
        pass

    def slice_fail_ultimate(self, incisor: (object, object, object)):
        '''The ultimate fallback for unrecognised slice types.'''
        pass


class Sampleable(Basic):

    CHANNELS = (('sample', _query.Sample),)
    MULTICHANNELS = (('bounds', _query.Bounds),)

    def handle_slice(self, incisor: slice, /, *, caller):
        inc1 = _query.Bounds(incisor.start, incisor.stop)
        inc2 = _query.Sample(incisor.step)
        part = caller.__incise__(inc1, caller=caller)
        return part.__incise__(inc2, caller=part)

    def bounds_trivial_none(self, incisor: (type(None), type(None)), /):
        pass

    def bounds_fail_ultimate(self, incisor: (object, object), /):
        pass

    def handle_sample(self, incisor: _query.Sample, /, *, caller):
        incisor = incisor.content
        return self.samplegetmeths[type(incisor)](
            self, incisor, caller=caller
            )

    def sample_trivial_none(self, incisor: type(None), /):
        pass

    def sample_fail_ultimate(self, incisor: object, /):
        pass


class Multi(Basic):

    @property
    def labels(self, /):
        return self.bound.labels

    @property
    def choras(self, /):
        return self.bound.choras

    @property
    def depth(self, /):
        return len(self.choras)

    @property
    @_caching.soft_cache()
    def active(self, /):
        return tuple(
            not isinstance(cho, _incision.Degenerate) for cho in self.choras
            )

    @property
    @_caching.soft_cache()
    def activechoras(self, /):
        return tuple(_itertools.compress(self.choras, self.active))

    @property
    def activedepth(self, /):
        return len(self.activechoras)

    @property
    def degenerate(self, /):
        return self.activedepth <= 1

    def _handle_generic(self, incisor, /, *, caller, meth):
        choras = tuple(meth(incisor))
        if all(isinstance(chora, _incision.Degenerate) for chora in choras):
            return caller.__incise_retrieve__((
                tuple(chora.retrieve() for chora in choras),
                self.labels,
                ))
        if len(set(choras)) == 1:
            slyce = self.boundowner(choras[0], self.labels)
        else:
            slyce = self.boundowner(choras, self.labels)
        return caller.__incise_slyce__(slyce)

    def yield_mapping_multiincise(self, incisors: _collabc.Mapping, /):
        choras, keys = self.choras, self.labels
        for key, chora in zip(keys, choras):
            if key in incisors:
                yield chora.__incise__(
                    incisors[key], caller=_incision.Degenerator(chora)
                    )
            else:
                yield chora

    def yield_single_multiincise(self, incisor, /):
        chorait = iter(self.choras)
        while True:
            chora = next(chorait)
            if isinstance(chora, _incision.Degenerate):
                yield chora
            else:
                yield _incision.Degenerator(chora)[incisor]
                break
        else:
            assert False
        yield from chorait

    def yield_sequence_multiincise(self, incisors: _collabc.Sequence, /):
        ncho = self.activedepth
        ninc = len(incisors)
        nell = incisors.count(...)
        if nell:
            ninc -= nell
            if ninc % nell:
                raise ValueError("Cannot resolve incision ellipses.")
            ellreps = (ncho - ninc) // nell
        chorait = iter(self.choras)
        try:
            for incisor in incisors:
                if incisor is ...:
                    count = 0
                    while count < ellreps:
                        chora = next(chorait)
                        if not isinstance(chora, _incision.Degenerate):
                            count += 1
                        yield chora
                    continue
                while True:
                    chora = next(chorait)
                    check = isinstance(chora, _incision.Incisable)
                    assert check, (self, chora)
                    if isinstance(chora, _incision.Degenerate):
                        yield chora
                        continue
                    yield _incision.Degenerator(chora)[incisor]
                    break
        except StopIteration:
            raise ValueError("Too many incisors in tuple incision.")
        yield from chorait

    def handle_mapping(self, incisor: _Binding, /, *, caller, shallow=False):
        if not incisor:
            return caller.__incise_trivial__()
        if shallow:
            meth = self.yield_mapping_multiincise
        elif self.activedepth == 1:
            meth = self.yield_single_multiincise
        else:
            meth = self.yield_mapping_multiincise
        return self._handle_generic(incisor, caller=caller, meth=meth)

    def handle_sequence(self, incisor: tuple, /, *, caller, shallow=False):
        if not incisor:
            return caller.__incise_trivial__()
        if shallow:
            meth = self.yield_sequence_multiincise
        elif self.activedepth == 1:
            meth = self.yield_single_multiincise
        else:
            meth = self.yield_sequence_multiincise
        return self._handle_generic(incisor, caller=caller, meth=meth)

    def handle_shallow(self, incisor: _query.Shallow, /, *, caller):
        incisor = incisor.query
        return self.getmeths[type(incisor)](self,
            incisor, caller=caller, shallow=True
            )

    def handle_other(self, incisor: object, /, *, caller):
        meth = self.yield_single_multiincise
        return self._handle_generic(incisor, caller=caller, meth=meth)

    def __contains__(self, arg, /):
        choras = self.choras
        if len(arg) != len(choras):
            return False
        elif isinstance(arg, _collabc.Mapping):
            for key, chora in zip(self.labels, choras):
                if key in arg:
                    if arg[key] not in chora:
                        return False
        else:
            for val, chora in zip(arg, self.choras):
                if val not in chora:
                    return False
        return True

    def __includes__(self, arg, /):
        choras = self.choras
        if len(arg) != len(choras):
            return False
        elif isinstance(arg, _collabc.Mapping):
            for key, chora in zip(self.labels, choras):
                if key in arg:
                    if not chora.__includes__(arg[key]):
                        return False
        else:
            for val, chora in zip(arg, self.choras):
                if not chora.__includes__(val):
                    return False
        return True


###############################################################################
###############################################################################
