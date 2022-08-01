###############################################################################
''''''
###############################################################################


import abc as _abc

from .essence import Essence as _Essence
from .ousia import Ousia as _Ousia
from .system import System as _System
from .stele import Stele as _Stele


with _Stele:


    class AlgebraicType(_Essence):

        @classmethod
        def _yield_mroclasses(meta, /):
            yield from super()._yield_mroclasses()
            yield 'Base', ()
            yield 'Op', ('Base',)
            yield 'Unary', ('Op',)
            yield 'Variadic', ('Op',)


    class _AlgebraicTypeBase_(metaclass=AlgebraicType):


        class Base(metaclass=_Ousia):

            @classmethod
            @_abc.abstractmethod
            def convert(cls, arg, /):
                raise NotImplementedError


        class Op(metaclass=_Ousia):

            ...


        class Unary(metaclass=_System):

            arg: get('__corpus__.Base')

            @classmethod
            def __parameterise__(cls, /, *args, **kwargs):
                params = super().__parameterise__(*args, **kwargs)
                params.arg = cls.convert(params.arg)
                return params


        class Variadic(metaclass=_System):

            args: ARGS[get('__corpus__.Base')]

            @classmethod
            def __parameterise__(cls, /, *args, **kwargs):
                params = super().__parameterise__(*args, **kwargs)
                params.args = tuple(sorted(set(map(cls.convert, params.args))))
                return params


        @classmethod
        def __class_call__(cls, /, *args, **kwargs):
            return cls.Base(*args, **kwargs)

        @classmethod
        def __class_init__(cls, /):
            super().__class_init__()
            cls.register(cls.Base)
            setattr(cls.__corpus__, cls.__relname__.strip('_'), cls.Base)
            for name in cls.__mroclasses__:
                setattr(cls.__corpus__, name, getattr(cls, name))


###############################################################################
###############################################################################


#     __mroclasses__ = dict(
#         _Base_=(),
#         Op=('Base',),
#         Multi=('Op',),
#         Variadic=('Multi',),
#         )
