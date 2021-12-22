###############################################################################
''''''
###############################################################################


import abc as _abc

from everest import epitaph as _epitaph

from everest import exceptions as _exceptions


PROTOCOLMETHS = ('trivial', 'incise', 'retrieve', 'fail')


class IncisionException(_exceptions.ExceptionRaisedby):

    __slots__ = ('chora',)

    def __init__(self, chora=None, /, *args):
        self.chora = chora
        super().__init__(*args)

    def message(self, /):
        yield from super().message()
        yield 'during incision'
        chora = self.chora
        if chora is None:
            pass
        elif chora is not self.raisedby:
            yield ' '.join((
                f'via the hosted incisable `{repr(chora)}`',
                f'of type `{repr(type(chora))}`,',
                ))


class IncisorTypeException(IncisionException, TypeError):

    __slots__ = ('incisor',)

    def __init__(self, incisor, /, *args):
        self.incisor = incisor
        super().__init__(*args)
    
    def message(self, /):
        incisor = self.incisor
        yield from super().message()
        yield ' '.join((
            f'when object `{repr(incisor)}`',
            f'of type `{repr(type(incisor))}`',
            f'was passed as an incisor',
            ))


class Degenerate:

    __slots__ = ('value', '_epitaph')

    def __init__(self, value, /):
        self.value = value

    def getitem(self, arg=None, /, *, caller):
        if arg is None:
            return caller.retrieve(self.value)
        return caller.fail(self, arg)

    def get_epitaph(self, /):
        return _epitaph.TAPHONOMY.callsig_epitaph(type(self), self.value)

    @property
    def epitaph(self, /):
        try:
            return self._epitaph
        except AttributeError:
            out = self._epitaph = self.get_epitaph()
            return out

    def __repr__(self, /):
        return f"{type(self).__name__}({repr(self.value)})"


class IncisionHandler:

    def incise(self, chora, /):
        return chora

    def retrieve(self, index, /):
        return index

    def degenerate(self, index, /):
        return Degenerate(index)

    def trivial(self, /):
        return self

    def fail(self, chora, incisor, /):
        raise IncisorTypeException(incisor, chora, self)


DEFAULTHANDLER = IncisionHandler()


class Incisable(_abc.ABC, IncisionHandler):

    def __getitem__(self, arg, /):
        return self.getitem(arg, caller=self)

    @_abc.abstractmethod
    def getitem(self, arg, /, *, caller: IncisionHandler):
        raise NotImplementedError


class IncisableHost(Incisable):

    @property
    @_abc.abstractmethod
    def chora(self, /) -> Incisable:
        raise NotImplementedError

    @property
    def getitem(self, /):
        return self.chora.getitem


###############################################################################
###############################################################################
