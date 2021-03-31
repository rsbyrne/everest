###############################################################################
'''The module defining the funcy 'Inc' ur type.'''
###############################################################################

from .ur import Ur as _Ur

class Inc(_Ur):
    '''
    Wraps all funcy functions which are Slots
    or have at least one Slot term.
    '''
    @classmethod
    def __subclasshook__(cls, C):
        if cls is Inc:
            if any('get_value' in B.__dict__ for B in C.__mro__):
                if any('close' in B.__dict__ for B in C.__mro__):
                    return True
        return NotImplemented

###############################################################################
###############################################################################
