###############################################################################
''''''
###############################################################################

from .methadder import MethAdder as _MethAdder
from . import _wordhash

class HashIDable(_MethAdder):
    _hashID = None
    _hashint = None
    _hashstr = None
    @_MethAdder.decorate(property)
    def hashstr(self):
        hashval = self._hashstr
        if hashval is None:
            hashval = self._hashstr = _wordhash.quick_hash(self)
        return hashval
    @_MethAdder.decorate(property)
    def hashint(self):
        hashval = self._hashint
        if hashval is None:
            hashval = self._hashint = int(self.hashstr, 16)
        return hashval
    @_MethAdder.decorate(property)
    def hashID(self):
        hashval = self._hashID
        if hashval is None:
            if 'get_hashID' in dir(self):
                hashval = self.get_hashID() # pylint: disable=E1101
            else:
                hashval = _wordhash.word_hash(self)
            self._hashID = hashval
        return hashval

###############################################################################
###############################################################################
