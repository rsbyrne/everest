###############################################################################
''''''
###############################################################################


from .essence import Essence as _Essence


class Category(_Essence):

    ...


class _CategoryBase_(metaclass=Category):

    class Object(demiclass):

        ...

    class Morphism(demiclass):

        ...


###############################################################################
###############################################################################
