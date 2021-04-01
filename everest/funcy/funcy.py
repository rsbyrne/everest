###############################################################################
'''Defines the parent class of all funcy objects.'''
###############################################################################

from abc import ABC as _ABC, abstractmethod as _abstractmethod

class Funcy(_ABC):
    '''
    Parent class of all Funcy objects.
    '''
    def __init__(self, *args, **kwargs):
        self._initargs, self._initkwargs = args, kwargs
    @_abstractmethod
    def get_value(self):
        ...
    @property
    def value(self):
        return self.get_value()
    @value.setter
    def value(self, val, /):
        try:
            self.set_value(val)
        except AttributeError:
            raise TypeError(
                "Value deleting not supported for this Funcy function."
                )
    @value.deleter
    def value(self):
        try:
            self.del_value()
        except AttributeError:
            raise TypeError(
                "Value deleting not supported for this Funcy function."
                )
    def __str__(self):
        return str(self.value)
    @classmethod
    def _unreduce(cls, args, kwargs, state):
        obj = cls(*args, **kwargs)
        try:
            obj.set_value(state)
        except AttributeError:
            pass
        return obj
    def __reduce__(self):
        return (self._unreduce, (self._initargs, self._initkwargs, self.value))

###############################################################################
###############################################################################
