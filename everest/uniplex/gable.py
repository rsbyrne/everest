###############################################################################
''''''
###############################################################################


from everest.ptolemaic.schematic import Schematic as _Schematic

from .table import TableLike as _TableLike


class Gable(_TableLike, metaclass=_Schematic):

    dtype = str

    baseshape: tuple = (None,)


###############################################################################
###############################################################################
