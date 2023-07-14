###############################################################################
''''''
###############################################################################


from .essence import Essence as _Essence
from .algebra import Algebra as _Algebra
from .sett import Sett as _Sett
from .brace import Brace as _Brace


class Objj(metaclass=_Algebra):


    __mroclasses__ = dict(
        Sett=_Sett,
        Brace=_Brace,
        )




###############################################################################
###############################################################################
