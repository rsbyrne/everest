from ..base import Datalike

class Qualified(Datalike):
    @property
    def qualKeys(self):
        ignore, *keys = self._qualKeys()
        return keys
    def _qualKeys(self):
        yield None
