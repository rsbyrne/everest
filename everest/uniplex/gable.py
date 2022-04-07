###############################################################################
''''''
###############################################################################


from everest.ptolemaic.sprite import Sprite as _Sprite

from .table import TableLike as _TableLike


class Gable(_TableLike, metaclass=_Sprite):

    dtype = str

    baseshape: tuple = (None,)


###############################################################################
###############################################################################
