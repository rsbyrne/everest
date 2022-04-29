###############################################################################
''''''
###############################################################################


from everest import incision as _incision

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.pentheros import Pentheros as _Pentheros
from everest.ptolemaic.ousia import Ousia as _Ousia

from .algebraic import (
    Algebraic as _Algebraic, ALGEBRAICMETHODS as _ALGEBRAICMETHODS
    )
from .armature import Armature as _Armature


class TrivialException(Exception):
    ...


CHORAMETHODS = (
    '__pow__', '__rpow__',
    '__matmul__', '__rmatmul__',
    '__lshift__', '__rshift__',
    *_incision.INCISABLEMETHS,
    *_ALGEBRAICMETHODS,
    )


class Chora(_incision.Incisable, _Algebraic):
    '''The `Chora` type is the Ptolemaic implementation '''
    '''of the Everest 'incision protocol'. '''
    '''`Chora` objects can be thought of as representing 'space' '''
    '''in both concrete and abstract ways.'''


    MROCLASSES = ('Gen', 'Var', 'Empty', 'Degenerate')

    @property
    def __incise_empty__(self, /):
        return self.Empty

    @property
    def __incise_degenerate__(self, /):
        return self.Degenerate

    @property
    def __incision_chain__(self, /):
        return ChoraChain

    @property
    def __armature_generic__(self, /):
        return self.Gen

    @property
    def __armature_variable__(self, /):
        return self.Var

    def __pow__(self, arg, /):
        return self.__armature_brace__(self.__incise_trivial__(), arg)

    def __rpow__(self, arg, /):
        return NotImplemented

    def __matmul__(self, arg, /):
        return Composition(self.__incise_trivial__(), arg)

    def __rmatmul__(self, arg, /):
        return NotImplemented

    def __lshift(self, other, /):
        return AbstractMapping(other, self)

    def __rshift__(self, other, /):
        return AbstractMapping(self, other)


    class Gen(_Armature, metaclass=_Pentheros):
        ...


    class Var(_Armature, metaclass=_Ousia):

        _req_slots__ = ('_value',)
        _var_slots__ = ('value',)

        _default = None

        @property
        def value(self, /):
            try:
                return self._value
            except AttributeError:
                val = self._default
                self._alt_setattr__('_value', val)
                return val

        @value.setter
        def value(self, val, /):
            if val not in self.basis:
                raise ValueError(val)
            self._alt_setattr__('_value', val)

        @value.deleter
        def value(self, /):
            self._alt_setattr__('_value', self._default)


    @_incision.Degenerate.register
    class Degenerate(_incision.Incisable, _Armature, metaclass=_Pentheros):

        arg: object

        def retrieve(self, /):
            return self.arg

        def __incise__(self, incisor, /, *, caller):
            if incisor is Ellipsis:
                return caller.__incise_trivial__()
            return caller.__incise_fail__(
                incisor,
                "Cannot further incise an already degenerate incisable."
                )

        @property
        def __getitem__(self, /):
            raise ValueError("Cannot incise a degenerate.")

        @property
        def __contains__(self, /):
            return self.retrieve().__eq__

        def __includes__(self, _, /):
            return False


    @_incision.Empty.register
    class Empty(_incision.Incisable, _Armature, metaclass=_Pentheros):

        chora: _incision.Incisable

        def __incise__(self, incisor, /, *, caller):
            return caller.__incise_fail__(
                incisor,
                "Cannot further incise an empty incisable."
                )

        @property
        def __getitem__(self, /):
            raise ValueError("Cannot incise a degenerate.")

        def __contains__(self, _, /):
            return False


class AbstractMapping(Chora, metaclass=_Pentheros):

    fromchora: Chora
    tochora: Chora

    def __incise_retrieve__(self, incisor, /):
        return ArbitraryPair(self, *incisor)

    def __incise_slyce__(self, incisor, /):
        return AbstractMapping(*incisor)

    def __incise__(self, incisor, /, *, caller):
        if incisor is Ellipsis:
            return caller.__incise_trivial__()
        if not isinstance(incisor, tuple):
            return caller.__incise_fail__(
                incisor, "Incisors must be two-tuples."
                )
        if len(incisor) != 2:
            return caller.__incise_fail__(
                incisor, "Incisors must be two-tuples."
                )
        try:
            outs = tuple(
                _incision.Degenerator(chora)[subinc]
                for subinc, chora in zip(incisor, self.params.values())
                )
        except _incision.IncisorTypeException as exc:
            return caller.__incise_fail__(exc)
        if all(isinstance(out, _incision.Degenerate) for out in outs):
            return caller.__incise_retrieve__(out.retrieve() for out in outs)
        return caller.__incise_slyce__(outs)

    def __contains__(self, arg, /):
        if not isinstance(arg, ArbitraryPair):
            return False
        return self.__includes__(arg.source)

    def __includes__(self, arg, /):
        if not isinstance(arg, AbstractMapping):
            return False
        return all((
            self.fromchora.__includes__(arg.fromchora),
            self.tochora.__includes__(arg.tochora),
            ))


class ArbitraryPair(metaclass=_Pentheros):

    source: AbstractMapping
    key: object
    val: object

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        bound = super().parameterise(*args, **kwargs)
        source, key, val = bound.arguments.values()
        fromchora, tochora = source.params.values()
        if (key not in fromchora) or (val not in tochora):
            cls.paramexc(message=(
                "The `key` and `val` args must be proper members "
                "of the `source` `fromchora` and `tochora` respectively."
                ))
        return bound


class Composition(Chora, metaclass=_Pentheros):

    fobj: Chora
    gobj: Chora

    @property
    def __incise__(self, /):
        return self.gobj.__incise__

    def __incise_slyce__(self, incisor, /):
        return type(self)(self.fobj, self.gobj.__incise_slyce__(incisor))

    def __incise_retrieve__(self, incisor, /):
        return self.fobj[self.gobj.__incise_retrieve__(incisor)]

    for methname in _incision.COLLECTIONLIKEMETHS:
        exec('\n'.join((
            f"@property",
            f"def {methname}(self, /):",
            f"    return self.gobj.{methname}",
            )))
    del methname


class ChoraChain(_incision.IncisionChain):

    for methname in _ALGEBRAICMETHODS:
        exec('\n'.join((
            f"@property",
            f"def {methname}(self, /):",
            f"    return self.last.{methname}",
            )))
    del methname


class ChainChora(Chora, _incision.ChainIncisable):
    ...


@Chora.register
class DeferChora(_incision.DeferIncisable, metaclass=_Essence):

    for methname in _ALGEBRAICMETHODS:
        exec('\n'.join((
            f"@property",
            f"def {methname}(self, /):",
            f"    try:",
            f"        return self.__incision_manager__.{methname}",
            f"    except AttributeError:",
            f"        raise NotImplementedError",
            )))
    del methname




###############################################################################
###############################################################################
