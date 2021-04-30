###############################################################################
''''''
###############################################################################

from . import _classtools

from .makehash import word_hash, quick_hash

@property
def hashstr(self):
    hashval = self._hashstr
    if hashval is None:
        hashval = self._hashstr = quick_hash(self)
    return hashval

@property
def hashint(self):
    hashval = self._hashint
    if hashval is None:
        hashval = self._hashint = int(self.hashstr, 16)
    return hashval


@property
def hashID(self):
    hashval = self._hashID
    if hashval is None:
        if 'get_hashID' in dir(self):
            hashval = self.get_hashID()
        else:
            hashval = word_hash(self)
        self._hashID = hashval
    return hashval


class Hashclass(_classtools.MethAdder):
    _hashID = None
    _hashint = None
    _hashstr = None
    hashID = hashID
    hashstr = hashstr
    hashint = hashint
    @classmethod
    def __subclasshook__(cls, C):
        if cls is Hashclass:
            return cls.check_sub(C)
        return NotImplemented

###############################################################################
###############################################################################
