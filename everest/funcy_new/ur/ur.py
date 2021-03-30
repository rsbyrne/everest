###############################################################################
'''Defines the parent class of all funcy 'ur' types.'''
###############################################################################

from . import _Funcy

class Ur(_Funcy):
    '''The parent class of all funcy 'ur' types.'''
    def __init__(self, *args, wrapped = None, **kwargs):
        if not wrapped is None:
            self.wrapped = wrapped
        super().__init__(*args, **kwargs)
    @property
    def value(self):
        return self.wrapped.value

###############################################################################
###############################################################################
