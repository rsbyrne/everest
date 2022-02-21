###############################################################################
'''Defines the overarching exceptions inherited by all Everest code.'''
###############################################################################


class EverestException(Exception):
    '''Parent exception of all Everest exceptions.'''

    def __init__(self, /, message=''):
        self.usermessage = message

    @classmethod
    def trigger(cls, /, *args, **kwargs):
        raise cls(*args, **kwargs)

    def message(self, /):
        yield '\nSomething went wrong within Everest'

    def __str__(self, /):
        out = ''
        indent = 0
        for message in map(str, self.message()):
            if not message:
                continue
            for spec in (':', '.'):
                if message.endswith(spec):
                    specialend = spec
                    message = message[:-1]
                    break
            else:
                specialend = ''
            if message.endswith('\\'):
                message = message[:-1]
            elif specialend:
                message += specialend
            if message:
                out += '\n' + indent * '    ' + message
            if specialend == ':':
                indent += 1
            elif specialend == '.':
                indent = max(0, indent - 1)
        if (usermessage := self.usermessage):
            out += f"\n{'-'*70}\n{usermessage}\n{'-'*70}"
        if not out.endswith('.'):
            out += '.'
        return out


class ExceptionRaisedBy(EverestException):

    def __init__(self, /, raisedby=None, *args, **kwargs):
        self.raisedby = raisedby
        super().__init__(*args, **kwargs)

    def message(self, /):
        yield from super().message()
        raisedby = self.raisedby
        if raisedby is not None:
            yield 'within the object:'
            yield repr(raisedby) + '\.'
            yield 'of type:'
            yield repr(type(raisedby)) + '\.'


class MissingAsset(EverestException):
    '''Signals that something needs to be provided.'''


class NotYetImplemented(EverestException):
    '''Dev exception for a feature not yet implemented.'''


class IncisionException(EverestException):

    def message(self, /):
        yield from super().message()
        yield 'during incision'


class IncisionProtocolException(
        ExceptionRaisedBy, IncisionException, AttributeError
        ):

    def __init__(self, /, protocol, *args, **kwargs):
        self.protocol = protocol
        super().__init__(*args, **kwargs)

    def message(self, /):
        yield from super().message()
        yield ':'
        yield 'the protocol:'
        yield repr(self.protocol) + '\.'
        yield 'is not supported on this object.'


class IncisorTypeException(ExceptionRaisedBy, IncisionException):

    def __init__(self, /, incisor, *args, **kwargs):
        self.incisor = incisor
        super().__init__(*args, **kwargs)
    
    def message(self, /):
        incisor = self.incisor
        yield from super().message()
        yield 'when object:'
        yield repr(incisor) + '\.'
        yield 'of type:'
        yield repr(type(incisor)) + '\.'
        yield 'was passed as an incisor.'


class FrozenAttributesException(EverestException, AttributeError):
    ...


###############################################################################
###############################################################################
