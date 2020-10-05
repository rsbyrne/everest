from ._indexer import Indexer
from ..pyklet import Pyklet

class Stamper(Pyklet):
    def __init__(self, *args, hashID = None, **kwargs):
        if hashID is None:
            raise Exception(
                "Classes inheriting from Stamper must provide hashID."
                )
        super().__init__(*args, **kwargs)
        self.hashID = hashID
    def stamp(self, stampee):
        stampee._receive_stamp(self)

class Stampable(Indexer):

    _defaultStampsKey = 'stamps'

    def __init__(self,
            **kwargs
            ):

        self.stampsKey = self._defaultStampsKey
        self.stamps_stored = []

        super().__init__(**kwargs)

    def _receive_stamp(self, stamper):
        assert isinstance(stamper, Stamper), "Only Stampers may stamp."
        newStamp = (stamper.hashID, self.indexer, stamp)
        if not newStamp in self.stamps:
            self.stamps_stored.append(newStamp)
        self._stamp_sort(self.stamps_stored)

    @property
    def stamps(self):
        stamps = [*self.stamps_stored, *self.stamps_disk]
        self._stamp_sort(stamps)
        return stamps
    @property
    def stamps_disk(self):
        try:
            stamps = self.reader[self.stampsKey]
            self._stamp_sort(stamps)
            return stamps
        except (KeyError, NoActiveAnchorError):
            return []
    def _stamp_sort(self, stamps):
        stamps.sort(key = lambda row: row[1])

    def _save(self):
        super()._save()
        self.writer.add(self.stamps, 'stamp')
        self.stored_stamps.clear()
