###############################################################################
''''''
###############################################################################


from everest.ptolemaic.compound import Compound as _Compound

from .table import TableLike as _TableLike


class Gable(_TableLike, metaclass=_Compound):

    dtype = str

    baseshape: tuple = (None,)


###############################################################################
###############################################################################
