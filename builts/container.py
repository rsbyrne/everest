import hashlib
import time
import pickle
from collections import OrderedDict

from . import load
from . import check_global_anchor
from ._mutator import Mutator
from ..exceptions import EverestException
from .. import mpi

class Ticket:
    def __init__(self, obj, spice = 0, timestamp = None):
        from . import Built
        if timestamp is None:
            timestamp = mpi.share(time.time())
        if isinstance(obj, Built): hashID = obj.hashID
        elif type(obj) is str: hashID = obj
        else: raise TypeError
        if spice is None: spice = timestamp
        hashInp = hashID + str(spice)
        hexID = hashlib.md5(hashInp.encode()).hexdigest()
        hashVal = int(hexID, 16)
        self.spice = spice
        self.obj = obj
        self.hashID = hashID
        self.number = hashVal
        self.timestamp = timestamp
    def __repr__(self):
        return '<' + self.hashID + ';' + str(self.timestamp) + '>'
    def __reduce__(self):
        return (
            self.__class__,
            (self.hashID, self.spice, self.timestamp)
            )
    def __hash__(self):
        return self.number
    def __eq__(self, arg):
        if not isinstance(arg, Ticket): raise TypeError
        return self.hashID == arg.hashID
    def __lt__(self, arg):
        if not isinstance(arg, Ticket): raise TypeError
        return self.timestamp < arg.timestamp
    def __call__(self):
        if type(self.obj) is str:
            obj = load(self.obj)
        else:
            obj = self.obj
            self.obj = obj.hashID
        return obj

class ContainerError(EverestException):
    pass
class ContainerNotInitialisedError(EverestException):
    pass

class ContainerAccess:
    def __init__(self, reader, writer, hashID, projName):
        self.reader, self.writer, self.hashID, self.projName = \
            reader, writer, hashID, projName
    def __enter__(self):
        while True:
            try:
                busy = self.reader[self.hashID, self.projName, '_busy_']
            except KeyError:
                busy = False
            if busy:
                time.sleep(1)
            else:
                self.writer.add(
                    {self.projName: {'_busy_': True}},
                    self.hashID
                    )
                break
    def __exit__(self, *args):
        self.writer.add(
            {self.projName: {'_busy_': False}},
            self.hashID
            )

def _container_access_wrap(func):
    def wrapper(self, *args, **kwargs):
        with ContainerAccess(
                self.reader,
                self.writer,
                self.hashID,
                self.projName
                ):
            output = func(self, *args, **kwargs)
        return output
    return wrapper

class Container(Mutator):

    script = '''_script_from everest.builts.container import Container as CLASS'''

    def __init__(self,
            iterable,
            **kwargs
            ):

        check_global_anchor()

        self.iterable = iterable
        self.initialised = False

        super().__init__(**kwargs)

        # Mutator attributes:
        self._update_mutateDict_fns.append(
            self._container_update_mutateFn
            )

    def _container_update_mutateFn(self):
        # expects @_container_access_wrap
        self._mutateDict[self.projName] = dict()
        for key in ('checkedOut', 'checkedBack', 'checkedFail', 'checkedComplete'):
            self._mutateDict[self.projName][key] = getattr(self, key)

    def _container_update_from_disk(self):
        # expects @_container_access_wrap
        l_out, l_back, l_comp = loads = [], [], []
        keys = ('checkedOut', 'checkedBack', 'checkedFail', 'checkedComplete')
        for key, empty in zip(keys, loads):
            try: empty[:] = self.reader[self.hashID, self.projName, key]
            except KeyError: pass
        self.checkedOut, self.checkedBack, self.checkedComplete = loads
        self._check_checks()

    def _check_checks(self):
        o, b, c = self.checkedOut, self.checkedBack, self.checkedComplete
        together = [*o, *b, *c]
        assert len(set(together)) == len(together), (o, b, c)

    @_container_access_wrap
    def checkBack(self, ticket):
        self._check_initialised()
        if not ticket in self.checkedOut:
            raise ContainerError(
                "Checked in object was never checked out!",
                ticket, self.checkedOut
                )
        self._container_update_from_disk()
        self.checkedOut.remove(ticket)
        self.checkedBack.append(ticket)
        self.mutate()
        mpi.message("Relinquished ticket:", ticket)

    @_container_access_wrap
    def checkFail(self, ticket):
        self._check_initialised()
        if not ticket in self.checkedOut:
            raise ContainerError(
                "Checked in object was never checked out!",
                ticket, self.checkedOut
                )
        self._container_update_from_disk()
        self.checkedOut.remove(ticket)
        self.checkedFail.append(ticket)
        self.mutate()
        mpi.message("Failed ticket:", ticket)

    @_container_access_wrap
    def complete(self, ticket):
        self._check_initialised()
        self._container_update_from_disk()
        self.checkedOut.remove(ticket)
        self.checkedComplete.append(ticket)
        self.mutate()
        mpi.message("Completed ticket:", ticket)

    def initialise(self, projName = 'anon'):
        self.projName = projName
        self.checkedOut = []
        self.checkedBack = []
        self.checkedFail = []
        self.checkedComplete = []
        self.iter = iter(self.iterable)
        self._initialise()
        self.initialised = True

    @_container_access_wrap
    def _initialise(self):
        self._container_update_from_disk()
        self.mutate()

    def _container_iter_finalise(self):
        del self.projName
        del self.checkedOut
        del self.checkedBack
        del self.checkedComplete
        del self.iter
        self.initialised = False
        raise StopIteration

    def _check_initialised(self):
        if not self.initialised: raise ContainerNotInitialisedError

    def _ticket_checked(self, ticket):
        return any([
            ticket in checked \
                for checked in [
                    self.checkedOut,
                    self.checkedBack,
                    self.checkedFail,
                    self.checkedComplete
                    ]
            ])

    @_container_access_wrap
    def __next__(self):
        self._check_initialised()
        self._container_update_from_disk()
        if len(self.checkedBack):
            ticket = self.checkedBack.pop(0)
        else:
            while True:
                try: ticket = Ticket(next(self.iter))
                except StopIteration: self._container_iter_finalise()
                if not self._ticket_checked(ticket): break
        self.checkedOut.append(ticket)
        self.mutate()
        mpi.message("Checking out ticket:", ticket)
        return ticket

    def __len__(self):
        try: return len(self.iter) + len(self.checkedBack)
        except: return 99999999

    def __iter__(self):
        return self
