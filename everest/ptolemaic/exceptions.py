###############################################################################
'''
Defines the classes or base classes
of all exceptions thrown within the Ptolemaic system.
'''
###############################################################################


from . import _exceptions


class PtolemaicException(_exceptions.EverestException):
    '''The base class of all exceptions thrown by the Ptolemaic system.'''

    __slots__ = ('raisedby',)

    def __init__(self, raisedby=None, /):
        self.raisedby = raisedby

    def message(self, /):
        yield from super().message()
        raisedby = self.raisedby
        if raisedby is None:
            yield 'within the Ptolemaic system'
        else:
            yield 'within the Ptolemaic class:'
            yield repr(raisedby)


class ParameterisationException(PtolemaicException):

    def message(self, /):
        yield from super().message()
        yield 'during parameterisation'


class InitialisationException(PtolemaicException):

    def message(self, /):
        yield from super().message()
        yield 'during initialisation'


###############################################################################
###############################################################################
