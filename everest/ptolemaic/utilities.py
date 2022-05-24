###############################################################################
''''''
###############################################################################


class MultiType(type):

    def __new__(meta, /, *types):
        name = meta.__name__ + '_'.join(typ.__name__ for typ in types)
        return type.__new__(meta, name, (), dict(types=types))

    def __init__(cls, /, *args, **kwargs):
        super().__init__(cls.__name__, cls.__bases__, cls.__dict__)




class TypeBrace(MultiType):

    def __subclasscheck__(cls, arg: tuple, /):
        try:
            return all(issubclass(a, b) for a, b in zip(arg, cls.types))
        except TypeError:
            return False

    def __instancecheck__(cls, arg: tuple, /):
        try:
            return cls.__subclasscheck__(map(type, arg))
        except TypeError:
            return False


class TypeIntersection(MultiType):

    def __subclasscheck__(cls, arg: type, /):
        for typ in cls.types:
            if not issubclass(arg, typ):
                return False
        return True

    def __instancecheck__(cls, arg: object, /):
        return cls.__subclasscheck__(type(arg))


###############################################################################
###############################################################################
