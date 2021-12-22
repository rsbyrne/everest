###############################################################################
'''Defines the overarching exceptions inherited by all Everest code.'''
###############################################################################


class EverestException(Exception):
    '''Parent exception of all Everest exceptions.'''

    @classmethod
    def trigger(cls, /, *args, **kwargs):
        raise cls(*args, **kwargs)

    def message(self, /):
        yield '\nSomething went wrong within Everest'

    def __str__(self, /):
        return '\n'.join(map(str, self.message())) + '.'


class ExceptionRaisedby(EverestException):

    __slots__ = ('raisedby',)

    def __init__(self, raisedby=None, /):
        self.raisedby = raisedby

    def message(self, /):
        yield from super().message()
        raisedby = self.raisedby
        if raisedby is not None:
            yield ' '.join((
                f'within the object `{repr(raisedby)}`',
                f'of type `{repr(type(raisedby))}`',
                ))


class MissingAsset(EverestException):
    '''Signals that something needs to be provided.'''


class NotYetImplemented(EverestException):
    '''Dev exception for a feature not yet implemented.'''


###############################################################################
###############################################################################
