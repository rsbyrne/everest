###############################################################################
''''''
###############################################################################


from everest import ur as _ur

from .ousia import Ousia as _Ousia
from . import ptolemaic as _ptolemaic


class Eidos(_Ousia):

    ...


class _EidosBase_(metaclass=Eidos):

    @classmethod
    def _yield_getters(cls, /):
        return
        yield

    @classmethod
    def _yield_setters(cls, /):
        return
        yield

    @classmethod
    def _yield_deleters(cls, /):
        return
        yield

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls._getters = _ur.DatDict(cls._yield_getters())
        cls._setters = _ur.DatDict(cls._yield_setters())
        cls._deleters = _ur.DatDict(cls._yield_deleters())

    def __getattr__(self, name, /):
        cls = self.__ptolemaic_class__
        if name in cls.__req_slots__:
            try:
                getter = cls._getters[name]
            except KeyError as exc:
                raise AttributeError from exc
            val = getter(self)
            object.__setattr__(self, name, val)
            return val
        else:
            dct = self.__dict__
            try:
                return dct[name]
            except KeyError:
                pass
            try:
                getter = cls._getters[name]
            except KeyError as exc:
                raise AttributeError from exc
            val = dct[name] = getter(name)
            return val

    def __setattr__(self, name, val, /):
        cls = self.__ptolemaic_class__
        if name in cls._getters:
            raise AttributeError(
                "Cannot manually set a name "
                "that already has an associated getter method: "
                f"{name}"
                )
        try:
            setter = cls._setters[name]
        except KeyError:
            if name in cls.__req_slots__:
                if not self.__getattribute__('_mutable'):
                    raise AttributeError(
                        name, "Cannot alter slot while frozen."
                        )
                if not name.startswith('_'):
                    type(self).param_convert(val)
                object.__setattr__(self, name, val)
            else:
                try:
                    object.__setattr__(self, name, val)
                except AttributeError as exc:
                    if not name.startswith('_'):
                        type(self).param_convert(val)
                    self.__dict__[name] = val
        else:
            setter(self, val)

    def __delattr__(self, name, /):
        try:
            deleter = cls._deleters[name]
        except KeyError as exc:
            if name in cls.__req_slots__:
                if not self.__getattribute__('_mutable'):
                    raise AttributeError(
                        name, "Cannot alter slot while frozen."
                        )
                object.__delattr__(self, name)
            else:
                try:
                    object.__delattr__(self, name)
                except AttributeError:
                    try:
                        del self.__dict__[name]
                    except KeyError as exc:
                        raise AttributeError from exc
        else:
            deleter(self)


###############################################################################
###############################################################################


# import functools as _functools

# from .classbody import Directive as _Directive


# class AttrHandler(_Directive):

#     __slots__ = ('meth',)

#     @classmethod
#     def __body_call__(cls, body, arg=None, /, **kwargs):
#         if arg is None:
#             return _functools.partial(cls.__body_call__, body, **kwargs)
#         return cls(arg, **kwargs)

#     def __init__(self, meth, /):
#         self.meth = meth

#     def __directive_call__(self, body, name, /):
#         body[self.__class__.__name__.lower() + 's'][name] = self.meth


# class Getter(AttrHandler):

#     __slots__ = ('slot',)

#     def __init__(self, meth, /, *, slot=False):
#         super().__init__(meth)
#         self.slot = slot

#     def __directive_call__(self, body, name, /):
#         super().__directive_call__(body, name)
#         if self.slot:
#             body['__req_slots__'].append(name)


# class Setter(AttrHandler):

#     __slots__ = ()


# class Deleter(AttrHandler):

#     __slots__ = ()
