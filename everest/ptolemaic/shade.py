###############################################################################
''''''
###############################################################################


from .essence import Essence as _Essence

from .exceptions import PtolemaicException as _InitialisationException


class CannotInitialiseShade(_InitialisationException):

    def message(self, /):
        yield from super().message()
        yield '- you have tried to initialise a pure Shade subclass'
        yield 'but this is forbidden;'
        yield 'override __init__ or inherit from a class that does'
        yield 'to allow initialisation of your class.'


class Shade(metaclass=_Essence):
    '''
    Shade classes are compatible as bases for other classes.
    '''


###############################################################################
###############################################################################
