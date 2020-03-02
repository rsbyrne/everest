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
class TicketUnavailable(EverestException):
    pass

class Container(Unique, DiskBased):

    _swapscript = '''from everest.builts.container import Container as CLASS'''

    def __init__(self,
            iterable,
            **kwargs
            ):

        self.iterable = iterable
        self.initialised = False
        initTickets = {
            'out': [],
            'failed': [],
            'relinquished': [],
            'completed': []
            }

        super().__init__(tickets = initTickets, **kwargs)

    def initialise(self):
        self.iter = iter(self.iterable)
        self.initialised = True

    def _container_iter_finalise(self):
        del self.iter
        self.initialised = False
        raise StopIteration

    def _check_initialised(self):
        if not self.initialised: raise ContainerNotInitialisedError

    def _container_modify(self, ticket, name, op):
        x = self.reader[self.hashID, 'tickets', name]
        if op == 'append': x.append(ticket)
        elif op == 'remove': x.remove(ticket)
        self.writer.add(x, name, self.hashID, 'tickets')

    def relinquish(self, ticket):
        self._check_initialised()
        self._container_modify(ticket, 'relinquished', 'append')
        self._container_modify(ticket, 'out', 'remove')
        mpi.message("Relinquished ticket:", ticket)

    def fail(self, ticket, exception = None):
        self._check_initialised()
        self._container_modify(ticket, 'failed', 'append')
        self._container_modify(ticket, 'out', 'remove')
        mpi.message("Failed ticket:", ticket, exception)

    def complete(self, ticket):
        self._check_initialised()
        self._container_modify(ticket, 'completed', 'append')
        self._container_modify(ticket, 'out', 'remove')
        mpi.message("Completed ticket:", ticket)

    def get_relinquished(self):
        relinquished = self.reader[self.hashID, 'tickets', 'relinquished']
        if len(relinquished):
            ticket = relinquished[-1]
            self._container_modify(ticket, 'relinquished', 'remove')
            self._container_modify(ticket, 'out', 'append')
            return ticket
        else:
            raise NoCheckedBacks

    def checkout(self):
        ticket = Ticket(next(self.iter))
        tickets = self.reader[self.hashID, 'tickets']
        if not any([ticket in ts for tn, ts in sorted(tickets.items())]):
            self._container_modify(ticket, 'out', 'append')
            return ticket
        else:
            raise TicketUnavailable

    def __next__(self):
        self._check_initialised()
        while True:
            try:
                ticket = self.get_relinquished()
                break
            except NoCheckedBacks:
                try:
                    ticket = self.checkout()
                    break
                except TicketUnavailable:
                    pass
                except StopIteration:
                    self._container_iter_finalise()
        mpi.message("Checking out ticket:", ticket)
        return ticket

    def __len__(self):
        try: return len(self.iter) + len(self.checkedBack)
        except: return 99999999

    def __iter__(self):
        return self
