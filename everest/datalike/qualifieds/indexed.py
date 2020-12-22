from .base import Qualified

class Indexed(Qualified):
    @property
    def indexKeys(self):
        ignore, *keys = self._indexKeys()
        return keys
    def _indexKeys(self):
        yield None
    def _qualKeys(self):
        yield from super()._qualKeys()
        yield from self.indexKeys

class Counted(Indexed):
    countKey = 'count'
    def _indexKeys(self):
        yield from super()._indexKeys()
        yield self.countKey

class Chroned(Indexed):
    chronKey = 'count'
    def _indexKeys(self):
        yield from super()._indexKeys()
        yield self.chronKey
