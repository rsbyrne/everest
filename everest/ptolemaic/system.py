###############################################################################
''''''
###############################################################################


from . import _utilities

from .ptolemaic import Ptolemaic as _Ptolemaic
from .schema import Schema as _Schema


class System(_Ptolemaic, metaclass=_Schema):

    @classmethod
    def check_param(cls, arg, /):
        try:
            return super().check_param(arg)
        except cls.BadParameter:
            try:
                meth = cls.checktypes[type(arg)]
            except KeyError as exc:
                raise cls.BadParameter(arg) from exc
            else:
                return meth(arg)

    @classmethod
    def yield_checktypes(cls, /):
        return iter(())

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.checktypes = _utilities.TypeMap(cls.yield_checktypes())

    def _repr(self):
        return self.params.hashID

    def __init__(self, /):
        pass


###############################################################################
###############################################################################
