###############################################################################
'''
Defines the classes or base classes
of all exceptions thrown within the Ptolemaic system.
'''
###############################################################################


from everest import exceptions as _exceptions


class PtolemaicException(_exceptions.EverestException):
    '''The base class of all exceptions thrown by the Ptolemaic system.'''

    __slots__ = ('ptolemaic',)

    def __init__(self, ptolemaic=None, /):
        self.ptolemaic = ptolemaic

    def message(self, /):
        yield from super().message()
        ptolemaic = self.ptolemaic
        if ptolemaic is None:
            yield 'within the Ptolemaic system'
        else:
            yield ' '.join((
                f'within the Ptolemaic object `{repr(ptolemaic)}`',
                f'of type `{repr(type(ptolemaic))}`',
                ))


class ParameterisationException(PtolemaicException):

    __slots__ = ()

    def message(self, /):
        yield from super().message()
        yield 'during parameterisation'


class InitialisationException(PtolemaicException):

    __slots__ = ()

    def message(self, /):
        yield from super().message()
        yield 'during initialisation'


class IncisionException(PtolemaicException):

    __slots__ = ()

    def message(self, /):
        yield from super().message()
        yield 'during incision'


###############################################################################
###############################################################################
