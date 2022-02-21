###############################################################################
''''''
###############################################################################


from everest.primitive import Primitive as _Primitive

from everest.ptolemaic.diict import Namespace as _Namespace


class Attrs(_Namespace):

    def __setitem__(self, name, val, /):
        if not isinstance(name, _Primitive):
            raise TypeError(type(name))
        super().__setitem__(name, val)


###############################################################################
###############################################################################
