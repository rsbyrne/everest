import hashlib
import time
import pickle
import ast
from collections import OrderedDict

from . import load
from ._unique import Unique
from ._diskbased import DiskBased
from ..exceptions import EverestException
from .. import mpi
from .. import disk

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
        if not type(arg) is self.__class__: raise TypeError(arg, type(arg))
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
class NoCheckedBacks(EverestException):
    pass

class Container(Unique, DiskBased):

    _swapscript = '''from everest.builts.container import Container as CLASS'''

    def __init__(self,
            iterable,
            **kwargs
            ):

        self.iterable = iterable
        self.initialised = False

        super().__init__(**kwargs)

    def _read(self, key):
        # expects @disk.h5writewrap
        try:
            raw = self.h5file[self.hashID].attrs[key]
            return [pickle.loads(ast.literal_eval(inp)) for inp in raw]
        except KeyError:
            return []
    def _write(self, key, content):
        # expects @disk.h5writewrap
        out = [str(pickle.dumps(inp)) for inp in content]
        self.h5file[self.hashID].attrs[key] = out

    def _remove_from_checkedOut(self, ticket):
        # expects @disk.h5writewrap
        checkedOut = self._read('checkedOut')
        checkedOut.remove(ticket)
        self._write('checkedOut', checkedOut)

    def checkBack(self, ticket):
        self._checkBack(ticket)
        mpi.message("Relinquished ticket:", ticket)
    @disk.h5writewrap
    @mpi.dowrap
    def _checkBack(self, ticket):
        self._check_initialised()
        self._remove_from_checkedOut(ticket)
        checkedBack = self._read('checkedBack')
        checkedBack.append(ticket)
        self._write('checkedBack', checkedBack)

    def checkFail(self, ticket, exception = None):
        if not exception is None:
            ticket.exception = exception
        self._checkFail(ticket)
        mpi.message("Failed ticket:", ticket, exception)
    @disk.h5writewrap
    @mpi.dowrap
    def _checkFail(self, ticket):
        self._check_initialised()
        self._remove_from_checkedOut(ticket)
        checkedFail = self._read('checkedFail')
        checkedFail.append(ticket)
        self._write('checkedFail', checkedFail)

    def complete(self, ticket):
        self._complete(ticket)
        mpi.message("Completed ticket:", ticket)
    @disk.h5writewrap
    @mpi.dowrap
    def _complete(self, ticket):
        self._check_initialised()
        self._remove_from_checkedOut(ticket)
        checkedComplete = self._read('checkedComplete')
        checkedComplete.append(ticket)
        self._write('checkedComplete', checkedComplete)

    def initialise(self):
        self.iter = iter(self.iterable)
        self.initialised = True

    def _container_iter_finalise(self):
        del self.iter
        self.initialised = False
        raise StopIteration

    def _check_initialised(self):
        if not self.initialised: raise ContainerNotInitialisedError

    @disk.h5writewrap
    @mpi.dowrap
    def _check_ticket(ticket):
        self._container_update_from_disk()

    @disk.h5writewrap
    @mpi.dowrap
    def _get_checkedBack(self):
        checkedBack = self._read('checkedBack')
        if len(checkedBack):
            ticket = checkedBack.pop(0)
            self._write('checkedBack', checkedBack)
            return ticket
        else:
            raise NoCheckedBacks

    @disk.h5writewrap
    @mpi.dowrap
    def _check_available(self, ticket):
        checkedOut = self._read('checkedOut')
        checkedBack = self._read('checkedBack')
        checkedFail = self._read('checkedFail')
        checkedComplete = self._read('checkedComplete')
        checked = [*checkedOut, *checkedBack, *checkedFail, *checkedComplete]
        if ticket in checked:
            return False
        else:
            checkedOut.append(ticket)
            self._write('checkedOut', checkedOut)
            return True

    def __next__(self):
        self._check_initialised()
        while True:
            ticket = None
            try:
                ticket = self._get_checkedBack()
                break
            except NoCheckedBacks:
                try:
                    ticket = Ticket(next(self.iter))
                    if self._check_available(ticket):
                        break
                except StopIteration:
                    self._container_iter_finalise()
        mpi.message("Checking out ticket:", ticket)
        return ticket

    def __len__(self):
        try: return len(self.iter) + len(self.checkedBack)
        except: return 99999999

    def __iter__(self):
        return self
