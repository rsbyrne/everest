###############################################################################
''''''
###############################################################################


from collections import abc as _collabc
import inspect as _inspect
import functools as _functools

from everest import ur as _ur

from .smartattr import SmartAttr as _SmartAttr
from .content import Kwargs as _Kwargs


_pempty = _inspect._empty


class Organs(_Kwargs):

    ...


class Organ(_SmartAttr):

    ligatures: _collabc.Mapping = _ur.DatDict()

    __merge_fintyp__ = Organs

    @classmethod
    def __body_call__(cls, body, arg=None, /, **ligatures):
        if arg is None:
            return _functools.partial(cls.__body_call__, body, **ligatures)
        return cls(hint=arg, ligatures=ligatures)

    @staticmethod
    def process_ligatures(arg, /):
        return _ur.DatDict(arg)

    def _yield_arguments(self, instance, typ, /):
        ligatures = self.ligatures
        for nm, pm in typ.__signature__.parameters.items():
            try:
                val = ligatures[nm]
            except KeyError:
                try:
                    val = getattr(instance, nm)
                except AttributeError:
                    val = pm.default
                    if val is _pempty:
                        raise RuntimeError(f"Organ missing argument: {nm}")
            yield nm, val

    def __call__(self, instance, name, /):
        typ = self.hint
        params = typ.Params(**dict(
            self._yield_arguments(instance, typ)
            ))
        return typ.construct(params, _corpus_=(instance, name))

    def __directive_call__(self, body, name, /):
        super().__directive_call__(body, name)
        body['getters'][name] = lambda obj: self(obj, name)
        body[f"_{name}_"] = self.hint
        body['__req_slots__'].append(name)


###############################################################################
###############################################################################
