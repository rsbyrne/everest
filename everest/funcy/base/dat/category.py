################################################################################

from .dat import Dat as _Dat, QuickDat as _QuickDat

class Category(_Dat):
    ...
    
class QuickCategory(_QuickDat, Category):
    def __init__(self, value: str, /, **kwargs) -> None:
        super().__init__(value, **kwargs)

################################################################################