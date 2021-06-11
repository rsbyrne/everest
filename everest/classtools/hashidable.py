###############################################################################
''''''
###############################################################################


from .adderclass import AdderClass as _AdderClass
from . import _wordhash


@_AdderClass.wrapmethod
def extra_init(calledmeth, obj, *args, **kwargs):
    calledmeth(obj, *args, **kwargs)
    if 'get_hashID' in dir(obj):
        hashval = obj.get_hashID()  # pylint: disable=E1101
    else:
        hashval = _wordhash.word_hash(obj)
    obj._hashID = hashval  # pylint: disable=W0212


class HashIDable(_AdderClass):

    _hashID = None
    _hashint = None
    _hashstr = None
    toadd = dict(
        __init__=extra_init,
        )

    @_AdderClass.decorate(property)
    def hashstr(self):
        hashval = self._hashstr
        if hashval is None:
            hashval = self._hashstr = _wordhash.quick_hash(self)
        return hashval

    @_AdderClass.decorate(property)
    def hashint(self):
        hashval = self._hashint
        if hashval is None:
            hashval = self._hashint = int(self.hashstr, 16)
        return hashval

    @_AdderClass.decorate(property)
    def hashID(self):
        return self._hashID


###############################################################################
###############################################################################
