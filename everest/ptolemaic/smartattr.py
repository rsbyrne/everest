###############################################################################
''''''
###############################################################################


from abc import abstractmethod as _abstractmethod
from functools import partial as _partial
import inspect as _inspect
import types as _types

from everest.dclass import DClass as _DClass

from . import ptolemaic as _ptolemaic
from .sprite import Sprite as _Sprite
from .wisp import Kwargs as _Kwargs
from .essence import Any as _Any, Null as _Null
from .pathget import PathGet as _PathGet
from .enumm import Enumm as _Enumm


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


class ContentType(metaclass=_Enumm):

    UNKNOWN: None
    CLASSLIKE: None
    STATICLIKE: None
    CLASSMETHOD: None
    INSTANCEMETHOD: None


class SmartAttrHolder(_Kwargs):

    ...


class SmartAttrDirective(metaclass=_DClass):

    typ: type
    kwargs: dict
    content: ... = None

    def __directive_call__(self, body, name, /):
        content = self.content
        smartattr = self.typ(content=content, **self.kwargs)
        return smartattr.__directive_call__(body, name, content)


class SmartAttr(metaclass=_Sprite):

    __merge_dyntyp__ = dict
    __merge_fintyp__ = SmartAttrHolder

    hint: ... = NotImplemented
    note: str = NotImplemented

    @classmethod
    def _process_hint(cls, hint, /):
        if isinstance(hint, _PathGet):
            return hint
        elif isinstance(hint, type):
            if isinstance(hint, _ptolemaic.Ptolemaic):
                return hint
            raise TypeError(hint)
        if isinstance(hint, str):
            return _PathGet(hint)
        if isinstance(hint, tuple):
            return tuple(map(cls._process_hint, hint))
        if hint is Ellipsis:
            return _Any
        if hint is None:
            return _Null
        if hint is NotImplemented:
            return hint
        raise ValueError(hint)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        singlename = cls.__single_name__ = cls.__name__.lower()
        cls.__merge_name__ = f"__{singlename}s__"

    @classmethod
    def _parameterise_(cls, /, *args, content=None, **kwargs):
        params = super()._parameterise_(*args, **kwargs)
        if content is not None:
            cls.adjust_params_for_content(params, content)
        params.hint = cls._process_hint(params.hint)
        return params

    @classmethod
    def adjust_params_for_content_signature(cls, params, sig, contenttype):
        if params.hint is object:
            if (retanno := sig.return_annotation) is not sig.empty:
                params.hint = retanno

    @classmethod
    def adjust_params_for_content(cls, params, content, /):
        if isinstance(content, str):
            return
        if isinstance(content, _PathGet):
            return
        if isinstance(content, (staticmethod, _types.MethodType)):
            contenttype = ContentType.STATICLIKE
            content = content.__func__
        elif isinstance(content, classmethod):
            contenttype = ContentType.CLASSMETHOD
            content = content.__func__
        elif isinstance(content, _types.FunctionType):
            contenttype = ContentType.INSTANCEMETHOD
        elif isinstance(content, type):
            contenttype = ContentType.CLASSLIKE
        try:
            sig = _inspect.signature(content)
        except TypeError:
            pass
        else:
            cls.adjust_params_for_content_signature(params, sig, contenttype)
        if params.note == '':
            try:
                params.note = content.__doc__
            except AttributeError:
                pass

    @classmethod
    def _merge_smartattrs(cls, prev, current, /):
        return current

    def __directive_call__(self, body, name, /, content=NotImplemented):
        mergedct = body[self.__merge_name__]
        try:
            prev = mergedct[name]
        except KeyError:
            mergedct[name] = self
            body.enroll_shade(name)
        else:
            mergedct[name] = \
                self.__ptolemaic_class__._merge_smartattrs(prev, self)
        return name, content

    @classmethod
    def __body_call__(cls, body, content=None, /, **kwargs):
        if content is None:
            return _partial(cls.__body_call__, body, **kwargs)
        if isinstance(content, _PathGet):
            content = content(body.namespace)
        return SmartAttrDirective(cls, kwargs, content)

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
