###############################################################################
''''''
###############################################################################

from . import _classtools

from .functional import Functional as _Functional

from .exceptions import NotYetImplemented


@_classtools.Operable
class Operation(_Functional):


    __slots__ = ('operator',)

    def __init__(self, operator, /, *args, **kwargs):
        self.operator = operator
        self.register_argskwargs(operator) # pylint: disable=E1101
        super().__init__(*args, **kwargs)

    @classmethod
    def operate(cls, operator, *args, **kwargs):
        return cls(operator, *args, **kwargs)


    class Var:

        def get_value(self):
            return self.operator(*self.termsresolved) # pylint: disable=E1101
        def set_value(self, value):
            raise NotYetImplemented
        def del_value(self):
            raise NotYetImplemented


###############################################################################
###############################################################################
