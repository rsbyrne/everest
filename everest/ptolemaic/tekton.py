###############################################################################
''''''
###############################################################################


import inspect as _inspect
import itertools as _itertools
import weakref as _weakref
import functools as _functools
from collections import abc as _collabc

from everest.utilities import caching as _caching, FrozenMap as _FrozenMap
from everest import epitaph as _epitaph
from everest import chora as _chora

from everest.ptolemaic.bythos import Bythos as _Bythos
from everest.ptolemaic.ptolemaic import Ptolemaic as _Ptolemaic
from everest.ptolemaic import exceptions as _exceptions
from everest.ptolemaic import utilities as _utilities


@_utilities.add_defer_meths('arguments', like=dict)
class CallSig(_Ptolemaic):

    __slots__ = (
        'args', 'kwargs', 'arguments',
        )

    @classmethod
    def signature_call(cls, signature, args, kwargs, /):
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        return cls(bound.args, bound.kwargs, bound.arguments)

    def __init__(self, args, kwargs, arguments, /):
        super().__init__()
        self.args = args
        self.kwargs = _FrozenMap(kwargs)
        self.arguments = _FrozenMap(arguments)

    def get_epitaph(self, /):
        return (taph := self.taphonomy).custom_epitaph(
            *taph.posformat_callsig(
                type(self)._ptolemaic_class__,
                self.args, self.kwargs.content, self.arguments.content,
                )
            )

    @property
    def hexcode(self, /):
        return self.epitaph.hexcode

    @property
    def hashint(self, /):
        return self.epitaph.hashint

    @property
    def hashID(self, /):
        return self.epitaph.hashID

    def _repr(self, /):
        return ', '.join(map('='.join, zip(self, map(repr, self.values()))))

    @_caching.soft_cache()
    def __repr__(self, /):
        return f"<{self.__class__.__qualname__}({self._repr()})>"


class BadParameters(_exceptions.ParameterisationException):

    def __init__(self, owner: type, bads: tuple, /):
        self.bads = bads
        super().__init__(owner)

    def message(self, /):
        yield from super().message()
        yield "when one or more parameters failed the prescribed check:"
        for param in self.bads:
            yield f"{repr(param)}, {repr(type(param))}"


class Registrar(_Ptolemaic):
    '''
    Handles parameterisation and type checking
    on behalf of its outer class.
    '''

    __slots__ = ('owner', 'args', 'kwargs', 'bads')

    def __init__(self, owner: type, /):
        self.owner, self.args, self.kwargs, self.bads = owner, [], {}, []

    ### Serialisation:

    def get_epitaph(self, /):
        return (taph := self.taphonomy).custom_epitaph(
            *taph.posformat_callsig(
                type(self)._ptolemaic_class__,
                self.owner,
                )
            )

    ### Basic functionality to check and process parameters:

    @property
    def process_param(self, /):
        return self.owner.process_param

    @property
    def check_param(self, /):
        return self.owner.check_param

    def __call__(self, /, *args, **kwargs):
        self.args.extend(map(self.process_param, args))
        self.kwargs.update(zip(
            map(str, kwargs),
            map(self.process_param, kwargs.values())
            ))

    def finalise(self, /):
        callsig = CallSig.signature_call(
            self.owner.__signature__,
            self.args,
            self.kwargs,
            )
        if bads := tuple(_itertools.filterfalse(
                self.check_param,
                callsig.values(),
                )):
            raise BadParameters(self.owner, bads)
        return callsig

    ### Basic object legibility:

    def _repr(self, /):
        argtup = ', '.join(map(repr, self.args))
        kwargtup = ', '.join(
            f"{key}: {repr(val)}"
            for key, val in self.kwargs.items()
            )
        return f"*({argtup}), **{{{kwargtup}}}"


class TektonChora(_chora.Sliceable):

    __slots__ = ('signature',)

    def __init__(self, signature: _inspect.Signature, /):
        self.signature = signature
        super().__init__()

    def _retrieve_contains_(self, incisor: CallSig, /) -> CallSig:
        try:
            return CallSig.signature_call(
                self.signature,
                incisor.args,
                incisor.kwargs,
                )
        except TypeError as exc:
            raise KeyError from exc


class Tekton(_Bythos):

    @property
    @_caching.soft_cache('_cls_softcache')
    def __signature__(cls, /):
        return cls.get_signature()

    def call(cls, /):
        raise NotImplementedError

    def get_signature(cls, /):
        return _inspect.signature(cls.call)

    @property
    @_caching.soft_cache('_cls_softcache')
    def premade(cls, /):
        return _weakref.WeakValueDictionary()


class TektonBase(metaclass=Tekton):

    Registrar = Registrar
    ClassChora = TektonChora

    @classmethod
    def _get_classchora(cls, /) -> 'Chora':
        return cls.ClassChora(cls.__signature__)

    @classmethod
    def construct(cls, callsig: CallSig, /) -> _collabc.Hashable:
        return cls.call(*callsig.args, **callsig.kwargs)

    @classmethod
    def class_retrieve(cls, callsig: CallSig, /):
        if (hexcode := callsig.hexcode) in (pre := cls.premade):
            return pre[hexcode]
        out = cls.construct(callsig)
        pre[hexcode] = out
        return out

    @classmethod
    def process_param(cls, arg, /):
        return arg

    @classmethod
    def check_param(cls, arg, /):
        return True

    @classmethod
    def parameterise(cls, register, /, *args, **kwargs):
        register(*args, **kwargs)

    @classmethod
    def get_callsig(cls, /, *args, **kwargs):
        register = cls.Registrar(cls)
        cls.parameterise(register, *args, **kwargs)
        return register.finalise()

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return cls.class_retrieve(cls.get_callsig(*args, **kwargs))


###############################################################################
###############################################################################
