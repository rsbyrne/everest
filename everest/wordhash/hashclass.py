###############################################################################
''''''
###############################################################################

from abc import ABC as _ABC

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


class Hashclass(_ABC):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is Hashclass:
            if any('hashID' in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented
    def __new__(cls, ACls):
        '''Class decorator for designating a Hashclass.'''
        if not hasattr(ACls, '_hashID'):
            setattr(ACls, '_hashID', None)
        if not hasattr(ACls, '_hashint'):
            setattr(ACls, '_hashint', None)
        if not hasattr(ACls, '_hashstr'):
            setattr(ACls, '_hashstr', None)
        if not hasattr(ACls, 'hashID'):
            setattr(ACls, 'hashID', hashID)
        if not hasattr(ACls, 'hashstr'):
            setattr(ACls, 'hashstr', hashstr)
        if not hasattr(ACls, 'hashint'):
            setattr(ACls, 'hashint', hashint)
        return ACls

###############################################################################
###############################################################################
