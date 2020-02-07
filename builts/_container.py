import hashlib
import time
import pickle

from . import load
from . import check_global_anchor
from ._mutator import Mutator
from ..exceptions import EverestException
from .. import mpi

class Ticket:
    def __init__(self, obj, timestamp = None):
        from . import Built
        if isinstance(obj, Built): hashID = obj.hashID
        elif type(obj) is str: hashID = obj
        else: raise TypeError
        if timestamp is None: timestamp = mpi.share(time.time())
        hashInp = hashID + str(timestamp)
        hexID = hashlib.md5(hashInp.encode()).hexdigest()
        hashVal = int(hexID, 16)
        self.obj = obj
        self.hashID = hashID
        self.timestamp = timestamp
        self.number = hashVal
    def __reduce__(self):
        return (self.__class__, (self.hashID, self.timestamp))
    def __hash__(self):
        return hash(self.number)
    def __eq__(self, arg):
        if not isinstance(arg, Ticket): raise TypeError
        return self.number == arg.number
    def __lt__(self, arg):
        if not isinstance(arg, Ticket): raise TypeError
        return self.timestamp < arg.timestamp

class ContainerError(EverestException):
    pass

class Container(Mutator):

    from .container import __file__ as _file_

    def __init__(self,
            iterable = None,
            **kwargs
            ):

        check_global_anchor()

        self.iterable = iterable
        self.checkedOut = []
        self.checkedBack = []

        self.localObjects.update({
            'checkedOut': self.checkedOut,
            'checkedBack': self.checkedBack
            })

        super().__init__(**kwargs)

        # Mutator attributes:
        self._update_mutateDict_fns.append(
            self._container_updateFn
            )

    def _container_updateFn(self):
        self._check_anchored()
        for key in ('checkedOut', 'checkedBack'):
            loadedBytes = self.reader[self.hashID, key]
            loaded = [pickle.loads(x) for x in loadedBytes]
            pre = getattr(self, key)
            new = sorted(set([*loaded, *pre]))
            self._mutateDict[key] = new
            setattr(self, key, new)

    def restore(self, ticket):
        if not ticket in self.checkedOut:
            raise ContainerError("Restored object was never checked out!")
        self.checkedOut.remove(ticket)
        self.checkedBack.append(ticket)
        self.mutate()

    def complete(self, ticket):
        self.checkedOut.remove(ticket)
        self.mutate()

    def __next__(self):
        if not len(self): raise StopIteration
        if len(self.checkedBack):
            ticket = self.checkedBack.pop(-1)
        else:
            while True:
                ticket = Ticket(next(self.iterable))
                if not ticket in self.checkedOut: break
        self.checkedOut.append(ticket)
        if type(ticket.obj) is str:
            ticket.obj = load(ticket.obj)
        self.mutate()
        return ticket

    def __len__(self):
        try: return len(self.iterable) + len(self.checkedBack)
        except: return -1

    def __iter__(self):
        return self
