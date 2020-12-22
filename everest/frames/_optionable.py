from collections import OrderedDict

from cascade import Inputs

from ._subinstantiable import SubInstantiable

class Options(Inputs):
    pass

class Optionable(SubInstantiable):

    @classmethod
    def _helperClasses(cls):
        d = super()._helperClasses
        d['Options'] = ([Options,], OrderedDict())
        return d

    def __init__(self,
            **kwargs,
            ):
        self.options = self.Options(self.ghosts.options)
        super().__init__(**kwargs)
