###############################################################################
''''''
###############################################################################


from everest.ptolemaic.essence import Essence as _Essence


class Aspect(metaclass=_Essence):
    '''
    The base class of all Ptolemaic types.
    '''


class FunctionalMeta(_Essence):
    '''
    The metaclass of all `Functional` types:
    classes whose sole purpose is to be called like functions
    and which cannot be instantiated or inherited by `Ptolemaic` types.
    '''

    @property
    def __call__(cls):
        return cls.method

    class BASETYP(_Essence.BASETYP):

        def method(cls, /):
            raise NotImplementedError


class Functional(metaclass=FunctionalMeta):
    ...


###############################################################################
###############################################################################
