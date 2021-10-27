###############################################################################
''''''
###############################################################################


from .schema import Schema as _Schema

from .exceptions import PtolemaicException as _InitialisationException


class CannotInitialiseShade(_InitialisationException):

    def message(self, /):
        yield from super().message()
        yield '- you have tried to initialise a pure Shade subclass'
        yield 'but this is forbidden;'
        yield 'override __init__ or inherit from a class that does'
        yield 'to allow initialisation of your class.'


class Shade(metaclass=_Schema):
    '''
    Shade classes are compatible as bases for other classes.
    '''

    @classmethod
    def __class_init__(cls, /):
        cls.metacls.__class_init__(cls)

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        return cls.metacls.parameterise(cls, *args, **kwargs)

    @classmethod
    def instantiate(cls, params, /):
        return cls.metacls.instantiate(cls, params)

    @classmethod
    def construct(cls, /, *args, **kwargs):
        return cls.metacls.construct(cls, *args, **kwargs)

    @classmethod
    def _ptolemaic_getitem__(cls, arg, /):
        return cls.metacls._ptolemaic_getitem__(cls, arg)

    @classmethod
    def _ptolemaic_contains__(cls, arg, /):
        return cls.metacls._ptolemaic_contains__(cls, arg)

    @classmethod
    def _cls_repr(cls, /):
        try:
            meth = super()._cls_repr
        except AttributeError:
            return type(cls)._cls_repr(cls)
        return meth()

    def __init__(self, /):
        raise CannotInitialiseShade


###############################################################################
###############################################################################
