###############################################################################
'''
Defines the classes or base classes
of all exceptions thrown within the Ptolemaic system.
'''
###############################################################################


from everest.utilities import ArgsKwargs

from everest import exceptions as _exceptions


class PtolemaicException(_exceptions.EverestException):
    '''The base class of all exceptions thrown by the Ptolemaic system.'''


class PtolemaicExceptionRaisedBy(
        _exceptions.ExceptionRaisedBy,
        PtolemaicException,
        ):
    ...


class ParameterisationException(PtolemaicExceptionRaisedBy):

    def __init__(self, /, parameters=None, *args, **kwargs):
        if not parameters is None:
            _args, _kwargs = parameters
            parameters = ArgsKwargs(*_args, **_kwargs)
        self.parameters = parameters
        super().__init__(*args, **kwargs)

    def message(self, /):
        yield from super().message()
        yield 'during parameterisation'
        parameters = self.parameters
        if parameters is not None:
            yield 'when the following parameters were passed:'
            yield repr(parameters)


class InitialisationException(PtolemaicExceptionRaisedBy):

    def message(self, /):
        yield from super().message()
        yield 'during initialisation'


class IncisionException(PtolemaicExceptionRaisedBy):

    def __init__(self, /, chora=None, *args, **kwargs):
        self.chora = chora
        super().__init__(*args, **kwargs)

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

    def __init__(self, /, incisor, *args, **kwargs):
        self.incisor = incisor
        super().__init__(*args, **kwargs)
    
    def message(self, /):
        incisor = self.incisor
        yield from super().message()
        yield ' '.join((
            f'when object `{repr(incisor)}`',
            f'of type `{repr(type(incisor))}`',
            f'was passed as an incisor',
            ))


###############################################################################
###############################################################################
