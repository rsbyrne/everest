###############################################################################
''''''
###############################################################################


from functools import partial as _partial
import inspect as _inspect

from everest.armature import Armature as _Armature

from . import ptolemaic as _ptolemaic
from .sprite import Sprite as _Sprite
from .content import Kwargs as _Kwargs


def _fallback_getter(obj, name, instance, /):
    return obj

def _fallback_setter(obj, name, instance, val, /):
    raise AttributeError(
        f"Can't set attribute: {instance}, {name}"
        )

def _fallback_deleter(obj, name, instance, val, /):
    raise AttributeError(
        f"Can't set attribute: {instance}, {name}"
        )


class SmartAttrHolder(_Kwargs):

    ...


class SmartAttrDirective(metaclass=_Armature):

    typ: type
    kwargs: dict
    content: object = None

    def __directive_call__(self, body, name, /):
        return self.typ(**self.kwargs).__directive_call__(
            body, name, self.content
            )


class SmartAttr(metaclass=_Sprite):

    __merge_dyntyp__ = dict
    __merge_fintyp__ = SmartAttrHolder

    hint: None = None
    note: str = None

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        singlename = cls.__single_name__ = cls.__name__.lower()
        cls.__merge_name__ = f"__{singlename}s__"

    @classmethod
    def parameterise(cls, /, *args, content=None, **kwargs):
        params = super().parameterise(*args, **kwargs)
        if content is not None:
            cls.adjust_params_for_content(params, content)
        return params

    @classmethod
    def adjust_params_for_content(cls, params, content, /):
        if params.hint is NotImplemented:
            try:
                sig = inspect.signature(arg)
            except TypeError:
                pass
            else:
                retanno = sig.return_annotation
                if retanno is not sig.empty:
                    params.hint = retanno

    def __directive_call__(self, body, name, /, content=None):
        body[self.__merge_name__][name] = self
        body.enroll_shade(name)
        return name, content

    @classmethod
    def __body_call__(cls, body, arg=None,/, **kwargs):
        if arg is None:
            return _partial(cls.__body_call__, **kwargs)
        return SmartAttrDirective(cls, kwargs, arg)

    def _get_getter_(self, obj, name, /):
        try:
            meth = getattr(obj, f"__{self.__single_name__}_get__")
        except AttributeError:
            return _partial(_fallback_getter, name, obj)
        else:
            return _partial(meth, name)

    def _get_setter_(self, obj, name, /):
        try:
            meth = getattr(obj, f"__{self.__single_name__}_set__")
        except AttributeError:
            return _partial(_fallback_setter, name, obj)
        else:
            return _partial(meth, name)

    def _get_deleter_(self, obj, name, /):
        try:
            meth = getattr(obj, f"__{self.__single_name__}_delete__"),
        except AttributeError:
            return _partial(_fallback_deleter, name, obj)
        else:
            return _partial(meth, name)


###############################################################################
###############################################################################
