###############################################################################
'''Defines the overarching exceptions inherited by all Everest code.'''
###############################################################################


class EverestException(Exception):
    '''Parent exception of all Everest exceptions.'''

    def __init__(self, /, message=None):
        self._message = message

    @classmethod
    def trigger(cls, /, *args, **kwargs):
        raise cls(*args, **kwargs)

    def message(self, /):
        yield '\nSomething went wrong within Everest'

    def __str__(self, /):
        message = self._message
        if message is None:
            message = ''
        else:
            message = ('\n' + str(message)).replace('\n', '\n    ')
        return '\n'.join(map(str, self.message())) + ":" + message


class ExceptionRaisedBy(EverestException):

    def __init__(self, /, raisedby=None, *args, **kwargs):
        self.raisedby = raisedby
        super().__init__(*args, **kwargs)

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


class IncisionException(EverestException):

    def message(self, /):
        yield from super().message()
        yield 'during incision'


class IncisorTypeException(ExceptionRaisedBy, IncisionException):

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
