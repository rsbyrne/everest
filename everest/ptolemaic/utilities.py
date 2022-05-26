###############################################################################
''''''
###############################################################################


###############################################################################
###############################################################################


# class TypeBrace(type):

#     def __new__(meta, typ, /):
#         name = f"{meta.__name__}({typ})"
#         args = typ.__args__
#         typ = typ.__origin__
#         return type.__new__(meta, name, (), dict(args=args, typ=typ))

#     def __init__(cls, /, *args, **kwargs):
#         super().__init__(cls.__name__, cls.__bases__, cls.__dict__)

#     def __subclasscheck__(cls, typ: type, /):
#         try:
#             args = typ.__args__
#             typ = typ.__origin__
#         except AttributeError:
#             return False
#         if issubclass(typ, cls.typ):
#             return all(
#                 issubclass(a, b)
#                 for a, b in zip(args, cls.args)
#                 )
#         return False

#     def __instancecheck__(cls, arg: tuple, /):
#         return cls.__subclasscheck__(type(arg)[tuple(map(type, arg))])


# class TypeIntersection(type):

#     def __new__(meta, /, *types):
#         name = f"{meta.__name__}({types})"
#         return type.__new__(meta, name, (), dict(types=types))

#     def __init__(cls, /, *args, **kwargs):
#         super().__init__(cls.__name__, cls.__bases__, cls.__dict__)

#     def __subclasscheck__(cls, arg: type, /):
#         for typ in cls.types:
#             if not issubclass(arg, typ):
#                 return False
#         return True

#     def __instancecheck__(cls, arg: object, /):
#         return cls.__subclasscheck__(type(arg))
