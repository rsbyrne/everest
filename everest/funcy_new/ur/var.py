###############################################################################
'''The module defining the funcy 'Var' ur type.'''
###############################################################################

from . import _utilities

from .ur import Ur as _Ur

_unpacker_zip = _utilities.unpacker_zip

class Var(_Ur):
    '''
    Wraps all funcy functions which are Variable
    or have at least one Variable term.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.varterms = list(t for t in self.terms if isinstance(t, Var))
    def set_value(self, val, /):
        for term, _val in _unpacker_zip(self.varterms, val):
            term.set_value(_val)
    def del_value(self):
        for term in self.varterms:
            term.del_value()
    @classmethod
    def __subclasshook__(cls, C):
        if cls is Var:
            if any('get_value' in B.__dict__ for B in C.__mro__):
                if any('set_value' in B.__dict__ for B in C.__mro__):
                    return True
        return NotImplemented

###############################################################################
###############################################################################
