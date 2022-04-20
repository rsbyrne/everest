###############################################################################
''''''
###############################################################################


from everest import incision as _incision

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.ousia import Ousia as _Ousia

from .algebraic import (
    Algebraic as _Algebraic, ALGEBRAICMETHODS as _ALGEBRAICMETHODS
    )
from .armature import Armature as _Armature


class TrivialException(Exception):
    ...


CHORAMETHODS = (*_incision.INCISABLEMETHS, *_ALGEBRAICMETHODS)


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

    def __mod__(self, arg, /):
        return self.__armature_brace__(self.__incise_trivial__(), arg)

    def __rmod__(self, arg, /):
        return NotImplemented

    def __matmul__(self, arg, /):
        return Composition(self.__incise_trivial__(), arg)

    def __rmatmul__(self, arg, /):
        return NotImplemented


    class Gen(_Armature, metaclass=_Sprite):
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
    class Degenerate(_incision.Incisable, _Armature, metaclass=_Sprite):

        arg: object

        def retrieve(self, /):
            return self.arg

        def __incise__(self, incisor, /, *, caller):
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


    @_incision.Empty.register
    class Empty(_incision.Incisable, _Armature, metaclass=_Sprite):

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


class ChoraChain(_incision.IncisionChain):

    for methname in _ALGEBRAICMETHODS:
        exec('\n'.join((
            f"@property",
            f"def {methname}(self, /):",
            f"    return self.last.{methname}",
            )))
    del methname


class Composition(Chora, metaclass=_Sprite):

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
