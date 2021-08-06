###############################################################################
''''''
###############################################################################


from .chora import Chora as _Chora


class Bounded(_Chora):

    def __init__(self, *args, lbnd, ubnd, **kwargs):
        bnds = self.bnds = self.lbnd, self.ubnd = lbnd, ubnd
        assert not all(arg is None for arg in bnds)
        self.register_argskwargs(lbnd=lbnd, ubnd=ubnd)
        super().__init__(*args, **kwargs)


###############################################################################
###############################################################################
