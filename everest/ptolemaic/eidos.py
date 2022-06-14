###############################################################################
''''''
###############################################################################


import functools as _functools

from everest import ur as _ur

from .ousia import Ousia as _Ousia
from .classbody import Directive as _Directive


class AttrHandler(_Directive):

    __slots__ = ('meth',)

    @classmethod
    def __body_call__(cls, body, arg=None, /, **kwargs):
        if arg is None:
            return _functools.partial(cls.__body_call__, body, **kwargs)
        return cls(arg, **kwargs)

    def __init__(self, meth, /):
        self.meth = meth

    def __directive_call__(self, body, name, /):
        body[self.__class__.__name__.lower() + 's'][name] = self.meth


class Getter(AttrHandler):

    __slots__ = ('slot',)

    def __init__(self, meth, /, *, slot=False):
        super().__init__(meth)
        self.slot = slot

    def __directive_call__(self, body, name, /):
        super().__directive_call__(body, name)
        if self.slot:
            body['__req_slots__'].append(name)


class Setter(AttrHandler):

    __slots__ = ()


class Deleter(AttrHandler):

    __slots__ = ()


class Eidos(_Ousia):

    @classmethod
    def _yield_mergenames(meta, /):
        yield from super()._yield_mergenames()
        yield ('getters', dict, _ur.DatDict)
        yield ('setters', dict, _ur.DatDict)
        yield ('deleters', dict, _ur.DatDict)

    @classmethod
    def _yield_bodymeths(meta, /):
        yield from super()._yield_bodymeths()
        yield ('getter', Getter.__body_call__)
        yield ('setter', Setter.__body_call__)
        yield ('deleter', Deleter.__body_call__)


class _EidosBase_(metaclass=Eidos):


    def __getattr__(self, name, /):
        cls = self.__ptolemaic_class__
        if name in cls.__req_slots__:
            try:
                meth = cls.getters[name]
            except KeyError as exc:
                raise AttributeError from exc
            val = meth(self)
            object.__setattr__(self, name, val)
            return val
        dct = self.__dict__
        try:
            return dct[name]
        except KeyError:
            pass
        try:
            meth = cls.getters[name]
        except KeyError as exc:
            raise AttributeError from exc
        val = dct[name] = meth(self)
        return val

    def __setattr__(self, name, val, /):
        cls = self.__ptolemaic_class__
        if name in cls.getters:
            raise AttributeError(
                "Cannot manually set a name "
                "that already has an associated getter method: "
                f"{name}"
                )
        try:
            meth = cls.setters[name]
        except KeyError:
            if name in cls.__req_slots__:
                if not self.__getattribute__('_mutable'):
                    raise AttributeError(
                        name, "Cannot alter slot while frozen."
                        )
                object.__setattr__(self, name, val)
            else:
                try:
                    object.__setattr__(self, name, val)
                except AttributeError as exc:
                    self.__dict__[name] = val
        else:
            meth(self, val)

    def __delattr__(self, name, /):
        try:
            meth = cls.deleters[name]
        except KeyError as exc:
            if name in cls.__req_slots__:
                if not self.__getattribute__('_mutable'):
                    raise AttributeError(
                        name, "Cannot alter slot while frozen."
                        )
                object.__delattr__(self, name)
            else:
                try:
                    object.__setattr__(self, name, val)
                except AttributeError:
                    try:
                        del self.__dict__[name]
                    except KeyError as exc:
                        raise AttributeError from exc
        else:
            meth(self)


###############################################################################
###############################################################################
