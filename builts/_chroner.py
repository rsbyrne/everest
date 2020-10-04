import numpy as np
from functools import wraps

from ._producer import Producer, AbortStore, LoadFail
from ..value import Value
from ..anchor import NoActiveAnchorError

from .. import exceptions
class ChronerException(exceptions.EverestException):
    pass
class ChronAlreadyLoadedError(ChronerException):
    pass
class ChronerLoadFail(ChronerException, LoadFail):
    pass

class Chroner(Producer):

    _defaultChronsKey = 'chron'

    def __init__(self, **kwargs):
        self.chron = Value(-1)
        self.chronsKey = self._defaultChronsKey
        super().__init__(**kwargs)

    def _outkeys(self):
        for o in super()._outkeys(): yield o
        yield self.chronsKey
    def _out(self):
        for o in super()._out(): yield o
        yield self.chron.value

    @property
    def _chronsKeyIndex(self):
        return self.outkeys.index(self.chronsKey)
    @property
    def chrons_stored(self):
        storedChrons = sorted([
            row[self._chronsKeyIndex] for row in self.stored
            ])
        assert sorted(set(storedChrons)) == storedChrons
        return storedChrons
    @property
    def chrons_disk(self):
        try:
            chrons = self.readouts[self.chronsKey]
            assert len(set(chrons)) == len(chrons)
            chrons = [int(x) for x in chrons]
            return chrons
        except (KeyError, NoActiveAnchorError):
            return []
    @property
    def chrons(self):
        return sorted(set([*self.chrons_stored, *self.chrons_disk]))
    def _chroner_sort_stored_fn(self):
        self.stored.sort(key = lambda row: row[self._chronsKeyIndex])
    def drop_chron(self, chron):
        del self.stored[self.chrons_stored.index(chron)]
    def _store(self):
        if self.chron in self.chrons_stored:
            raise AbortStore
        super()._store()

    def _save(self):
        keepChrons = [
            self.chrons_stored.index(i)
                for i in self.chrons_stored
                    if not i in self.chrons_disk
            ]
        self.stored[:] = [self.stored[i] for i in keepChrons]
        super()._save()

    def _process_load_chron_arg(self, chron):
        if chron == self.chron:
            raise ChronAlreadyLoadedError
        elif chron < 0:
            if self.initialised:
                chron += self.chron
            else:
                chron = -chron
            return chron
        else:
            return chron
    def _chroner_load_wrapper(func):
        @wraps(func)
        def wrapper(self, chron, *args, **kwargs):
            chron = self._process_load_chron_arg(chron)
            return func(self, chron, *args, **kwargs)
        return wrapper
    @_chroner_load_wrapper
    def load_chron_stored(self, chron):
        return self.load_index_stored(self.chrons_stored.index(chron))
    @_chroner_load_wrapper
    def load_chron_disk(self, chron):
        return self.load_index_disk(self.chrons_disk.index(chron))
    def load_chron(self, chron):
        try:
            return self.load_chron_stored(chron)
        except ValueError:
            return self.load_chron_disk(chron)
    def _load_process(self, outs):
        outs = super()._load_process(outs)
        self.chron.value = outs.pop(self.chronsKey)
        return outs
    def _load(self, arg):
        if type(arg) is float:
            try:
                self.load_chron(arg)
            except ValueError:
                raise ChronerLoadFail
        else:
            super()._load(arg)
