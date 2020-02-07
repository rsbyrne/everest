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
    def __repr__(self):
        return '<' + self.hashID + ';' + str(self.timestamp) + '>'
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
    def __call__(self):
        if type(self.obj) is str:
            self.obj = load(self.obj)
        return self.obj

class ContainerError(EverestException):
    pass
class ContainerNotInitialisedError(EverestException):
    pass

class Container(Mutator):

    from .container import __file__ as _file_

    def __init__(self,
            iterable,
            **kwargs
            ):

        check_global_anchor()

        self.iterable = iterable
        self.initialised = False

        self._toRemove = None

        super().__init__(**kwargs)

        # Mutator attributes:
        self._update_mutateDict_fns.append(self._container_update_mutateFn)

    def _container_update_mutateFn(self):
        self._check_anchored()
        for key in ('checkedOut', 'checkedBack', 'checkedComplete'):
            if self.initialised:
                loaded = self.reader[self.hashID, key]
                pre = getattr(self, key)
                new = sorted(set([*loaded, *pre]))
                try:
                    new.remove(self._toRemove)
                    self._toRemove = None
                except (ValueError, TypeError):
                    pass
                self._mutateDict[key] = new
            else:
                new = []
                self._mutateDict[key] = new
            setattr(self, key, new)

    def checkBack(self, ticket):
        if not ticket in self.checkedOut:
            raise ContainerError("Checked in object was never checked out!")
        self._toRemove = ticket
        self.checkedBack.append(ticket)
        self.mutate()

    def complete(self, ticket):
        self._toRemove = ticket
        self.checkedComplete.append(ticket)
        self.mutate()

    def initialise(self):
        self.iter = iter(self.iterable)
        self.mutate()
        self.initialised = True

    def __next__(self):
        if not self.initialised:
            raise ContainerNotInitialisedError
        if len(self.checkedBack):
            ticket = self.checkedBack[0]
            self._toRemove = ticket
        else:
            while True:
                try:
                    ticket = Ticket(next(self.iter))
                except StopIteration:
                    self.initialised = False
                    raise StopIteration
                if not ticket in self.checkedOut: break
        self.checkedOut.append(ticket)
        self.mutate()
        return ticket

    def __len__(self):
        try: return len(self.iter) + len(self.checkedBack)
        except: return 99999999

    def __iter__(self):
        return self
