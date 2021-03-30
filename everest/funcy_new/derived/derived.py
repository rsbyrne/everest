###############################################################################
'''The module defining the parent class for all Derived types.'''
###############################################################################

from . import _Funcy, _ur_convert, _FuncyPrimitive

class Derived(_Funcy):
    '''The parent class of all funcy 'instruments'.'''
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj.__init__(*args, **kwargs)
        return _ur_convert(obj)
    def __init__(self, *terms, **kwargs):
        if not all(isinstance(v, _FuncyPrimitive) for v in kwargs.values()):
            raise TypeError("Kwargs must all be Primitive type.")
        terms = tuple(_ur_convert(t) for t in terms)
        self.terms, self.kwargs = terms, kwargs

###############################################################################
###############################################################################
