###############################################################################
''''''
###############################################################################

from . import wordhash as _wordhash, classtools as _classtools

def __reduce__(self):
    redargs = (type(self), self.args, self.kwargs)
    return self.unreduce, redargs # pylint: disable=W0212

def unreduce(redcls, args, kwargs):
    return redcls(*args, **dict(kwargs)) # pylint: disable=E1102

@_classtools.ApplyDecorator(property)
def _unreduce_property(_):
    return unreduce

def copy(self):
    return self._unreduce(self.args, self.kwargs) # pylint: disable=W0212

def get_hashcontents(self):
    return (type(self), self.args, self.kwargs)

class Reloadable(_wordhash.Hashclass):
    copy = copy
    get_hashcontents = get_hashcontents
    unreduce = _unreduce_property
    def __new__(cls, ACls):
        _ = super().__new__(cls, ACls)
        ACls.__reduce__ = __reduce__
        return ACls

###############################################################################
###############################################################################
