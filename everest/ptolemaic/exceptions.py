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


class ParameterisationException(
        _exceptions.ExceptionRaisedBy,
        PtolemaicException,
        ):

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


class InitialisationException(
        _exceptions.ExceptionRaisedBy,
        PtolemaicException,
        ):

    def message(self, /):
        yield from super().message()
        yield 'during initialisation'


###############################################################################
###############################################################################
