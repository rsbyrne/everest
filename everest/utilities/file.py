###############################################################################
''''''
###############################################################################


import weakref as _weakref
import os as _os

import h5py as _h5py

from everest.utilities.mpi import rank as _rank
from everest.utilities import reseed as _reseed


FILES = _weakref.WeakValueDictionary()

FILEMODES = {'r+', 'w', 'w-', 'a', 'r'}
READONLYMODES = {'r'}
WRITEMODES = FILEMODES.difference(READONLYMODES)


def check_modes(*modes):
    if not all(mode in FILEMODES for mode in modes):
        raise ValueError(f"File mode is not acceptable.")
    return not all((
        any(mode in READONLYMODES for mode in modes),
        any(mode in WRITEMODES for mode in modes),
        ))


class FileMeta(type):

    DEFAULTPATH = '~/'
    DEFAULTEXT = '.txt'

    ATTRNAMES = (
        'filepath', 'mode', 'lockfilepath'
        )

    def get_filepath(cls, name, /, path=None, ext=None):
        if path is None:
            path = cls.DEFAULTPATH
        path = _os.path.abspath(_os.path.expanduser(path))
        if ext is None:
            ext = cls.DEFAULTEXT
        return '.'.join((_os.path.join(path, name), ext))

    def __call__(cls, filepath, mode='a'):
        lockfilepath = f"{filepath}.lock"
        global FILES
        while True:
            try:
                file = FILES[filepath]
            except KeyError:
                try:
                    if _rank == 0:
                        with open(lockfilepath, 'x'):
                            pass
                except FileExistsError:
                    pass
                else:
                    file = FILES[filepath] = object.__new__(cls)
                    for attrname in cls.ATTRNAMES:
                        setattr(cls, attrname, eval(attrname))
                    file.__init__()
                    return file
            else:
                if check_modes(file.mode, mode):
                    if isinstance(file, cls):
                        return file
            _reseed.rsleep(0.01, 0.02)


class File(metaclass=FileMeta):

    __slots__ = (*FileMeta.ATTRNAMES, 'file', '__weakref__')

    def __init__(self, /):
        if _rank == 0:
            self.file = self._open_()

    def _open_(self, /):
        return open(self.filepath, self.mode)

    def _close_(self, /):
        self.file.close()

    def __del__(self, /):
        if _rank == 0:
            self._close_()
            _os.remove(self.lockfilepath)

    def __enter__(self, /):
        return _weakref.proxy(self)

    def __exit__(self, /, *_):
        pass


class H5File(File):

    DEFAULTEXT = 'h5'

    def _open_(self, /):
        return _h5py.File(self.filepath, self.mode)

    def _close_(self, /):
        self.file.flush()
        super()._close_()


###############################################################################
###############################################################################
