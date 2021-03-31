###############################################################################
'''The module defining the parent class of the Misc Variable type.'''
###############################################################################

from .variable import Variable as _Variable

class Misc(_Variable):
    _value = None
    def get_value(self):
        return self._value
    def set_value(self, val, /):
        self._value = val
    def del_value(self):
        self._value = None

###############################################################################
###############################################################################
