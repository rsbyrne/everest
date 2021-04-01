###############################################################################
'''The module defining the parent class of all 'Variable' Base types.'''
###############################################################################

from abc import abstractmethod as _abstractmethod

from . import _Base

class Variable(_Base):
    @_abstractmethod
    def set_value(self, val, /):
        ...
    @_abstractmethod
    def del_value(self):
        ...

###############################################################################
###############################################################################
