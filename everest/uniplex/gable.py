###############################################################################
''''''
###############################################################################


from everest.ptolemaic.pentheros import Pentheros as _Pentheros

from .table import TableLike as _TableLike


class Gable(_TableLike, metaclass=_Pentheros):

    dtype = str

    baseshape: tuple = (None,)


###############################################################################
###############################################################################
