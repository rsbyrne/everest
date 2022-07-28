###############################################################################
''''''
###############################################################################


import abc as _abc

from ..ptolemaic.essence import Essence as _Essence
from ..ptolemaic.ousia import Ousia as _Ousia
from ..ptolemaic.system import System as _System
from ..ptolemaic.stele import Stele as _Stele


with _Stele:


    class AlgebraicType(_Essence):

        @classmethod
        def _yield_mroclasses(meta, /):
            yield from super()._yield_mroclasses()
            yield 'Base', ()
            yield 'Op', ('Base',)
            yield 'Multi', ('Op',)
            yield 'Variadic', ('Multi',)


    class _AlgebraicTypeBase_(metaclass=AlgebraicType):


        class Base(metaclass=_Ousia):

            @classmethod
            @_abc.abstractmethod
            def convert(cls, arg, /):
                raise NotImplementedError


        class Op(metaclass=_Ousia):

            ...


        class Multi(metaclass=_Ousia):

            ...


        class Variadic(metaclass=_System):

            args: ARGS

            @classmethod
            def __parameterise__(cls, /, *args, **kwargs):
                params = super().__parameterise__(*args, **kwargs)
                params.args = tuple(sorted(set(map(cls.convert, params.args))))
                return params


        @classmethod
        def __class_call__(cls, /, *args, **kwargs):
            return cls._Base_(*args, **kwargs)

        @classmethod
        def __class_init__(cls, /):
            super().__class_init__()
            cls.register(cls.Base)
            print(cls.__relname__.strip('_'))
            setattr(cls.__corpus__, cls.__relname__.strip('_'), cls.Base)
            for name in cls.__mroclasses__:
                print(name)
                setattr(cls.__corpus__, name, getattr(cls, name))


###############################################################################
###############################################################################


#     __mroclasses__ = dict(
#         _Base_=(),
#         Op=('Base',),
#         Multi=('Op',),
#         Variadic=('Multi',),
#         )
