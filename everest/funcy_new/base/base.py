###############################################################################
'''The module defining the parent class for all Base types.'''
###############################################################################

from . import _Funcy, _reseed

class Base(_Funcy):
    def __init__(self, *, name = None, **kwargs):
        if name is None:
            name = f"anon_{_reseed.randint(1e11, 1e12 - 1)}"
        self.name = name = str(name)
        self.kwargs = kwargs = {**kwargs, 'name': name}
        super().__init__(**kwargs)
    def __repr__(self):
        return f"{self.__class__.__name__}{self.kwargs}"

###############################################################################
###############################################################################
