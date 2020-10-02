from functools import wraps
import os

from .writer import Writer
from .reader import Reader
from .disk import get_framePath, purge_address
from .exceptions import EverestException

class AnchorError(EverestException):
    '''
    Something went wrong relating to Frames and Anchors.
    '''
class NoActiveAnchorError(AnchorError):
    '''
    No active anchor could be found.
    '''
class GlobalAnchorRequired(EverestException):
    pass
class NestedAnchorError(EverestException):
    '''
    Cannot open an anchor inside itself.
    '''

GLOBALREADER, GLOBALWRITER = None, None
NAME, PATH = None, None
GLOBALANCHOR = False
def set_global_anchor(name, path, purge = False):
    global GLOBALANCHOR, NAME, PATH, GLOBALREADER, GLOBALWRITER
    NAME, PATH = name, os.path.abspath(path)
    fullPath = os.path.join(PATH, NAME + '.frm')
    if purge: disk.purge_address(NAME, PATH)
    GLOBALANCHOR = True
    GLOBALREADER, GLOBALWRITER = Reader(name, path), Writer(name, path)
def release_global_anchor():
    global GLOBALANCHOR, NAME, PATH, GLOBALREADER, GLOBALWRITER
    NAME, PATH = None, None
    GLOBALANCHOR = False
    GLOBALREADER, GLOBALWRITER = None, None
def check_global_anchor():
    global GLOBALANCHOR
    if not GLOBALANCHOR: raise GlobalAnchorRequired

def _namepath_process(name, path):
    global GLOBALANCHOR, NAME, PATH
    if GLOBALANCHOR:
        if not (
                (name is None or name == NAME) \
                and (path is None or path == PATH)
                ):
            raise Exception("Global anchor has been set!")
        name, path = NAME, PATH
    else:
        if (name is None) or (path is None):
            raise TypeError
    return name, os.path.abspath(path)


class Anchor:

    _activeAnchor = None

    @property
    def active(self):
        activeAnchor = self.__class__._activeAnchor
        if activeAnchor is None:
            raise NoActiveAnchorError
        return activeAnchor
    @active.setter
    def active(self, value):
        self.__class__._activeAnchor = value

    def __init__(self,
            name = None,
            path = None,
            purge = False,
            test = False
            ):
        self.name, self.path = _namepath_process(name, path)
        self.test, self.purge = test, purge
        self.open = False

    def purge(self):
        purge_address(self.name, self.path)

    def __enter__(self):
        if self.open:
            raise AlreadyAnchoredError
        self.open = True
        self._active = self.active
        self.active = self
        if self.purge or self.test:
            self.purge()
        self.writer = Writer(self.name, self.path)
        self.reader = Reader(self.name, self.path)
        self.globalwriter = Writer(self.name, self.path, '_globals_')
        self.globalreader = Reader(self.name, self.path, '_globals_')
        self.h5filename = get_framePath(self.name, self.path)
        return self

    def __exit__(self, *args):
        assert self.open
        self.open = False
        self.active = self._active
        if self.test:
            self.purge()
        del self.name, self.path, self.writer, self.reader, \
            self.globalwriter, self.globalreader, self.h5filename, \
            self.test, self.purge, self._active
