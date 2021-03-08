################################################################################

from . import _generic, _Gruple, _unpacker_zip
from .derived import Derived as _Derived

class Group(_Derived, _generic.FuncyStruct):

    def evaluate(self):
        return _Gruple(*self._resolve_terms())

    def __setitem__(self, ind: _generic.FuncyIncisor, val: object, /):
        ind = self._value_resolve(ind)
        if isinstance(ind, _generic.FuncyStrictIncisor):
            self.terms[ind].value = val
        else:
            ts = iter(self.terms[ind])
            for t, v in _unpacker_zip(ts, val):
                t.value = v
    def __delitem__(self, ind: _generic.FuncyIncisor):
        self[ind] = None

    def __len__(self):
        return len(self.terms)

################################################################################
