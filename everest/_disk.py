###############################################################################
''''''
###############################################################################


import os as _os
import sys as _sys
import shutil as _shutil
import importlib as _importlib
import time as _time
from functools import wraps as _wraps
import weakref as _weakref

import h5py as _h5py

from .utilities import reseed as _reseed
from .exceptions import EverestException as _EverestException
from .mpi import mpi_wrap as _mpi_wrap


PYTEMP = '.'
if not PYTEMP in _sys.path:
    _sys.path.append(PYTEMP)


@_mpi_wrap
def purge_address(filepath):
    if _os.path.exists(filepath):
        _os.remove(filepath)
    lockpath = filepath + '.lock'
    if _os.path.exists(lockpath):
        _os.remove(lockpath)


class AccessForbidden(_EverestException):
    pass


@_mpi_wrap
def tempname(length=16, extension=None):
    name = _reseed.rstr(length)
    if extension is not None:
        name += '.' + extension
    return name


@_mpi_wrap
def lock(filepath, password=None):
    lockpath = filepath + '.lock'
    if not _os.path.isdir(_os.path.dirname(lockpath)):
        raise FileNotFoundError(
            "Directory '" + _os.path.dirname(lockpath) + "' could not be found."
            )
    while True:
        try:
            with open(lockpath, 'x') as f:
                if not password is None:
                    f.write(password)
                return True
        except FileExistsError:
            if not password is None:
                try:
                    with open(lockpath, 'r') as f:
                        if f.read() == password:
                            return False
                        else:
                            raise AccessForbidden
                except FileNotFoundError:
                    pass
        except FileNotFoundError:
            raise FileNotFoundError("Something went wrong and we don't know what!")
        _reseed.rsleep(0.1, 5.)


@_mpi_wrap
def release(filepath, password=''):
    lockpath = filepath + '.lock'
    try:
        with open(lockpath, 'r') as f:
            if f.read() == password:
                _os.remove(lockpath)
            else:
                raise AccessForbidden
    except FileNotFoundError:
        pass


FILEMODES = {'r+', 'w', 'w-', 'a', 'r'}
READONLYMODES = {'r'}
WRITEMODES = FILEMODES.difference(READONLYMODES)


def compare_modes(*modes):
    if not all(mode in FILEMODES for mode in modes):
        raise ValueError(f"File mode is not acceptable.")
    clause1 = any(mode in READONLYMODES for mode in modes)
    clause2 = any(mode in WRITEMODES for mode in modes)
    if clause1 and clause2:
        raise ValueError(f"File modes incompatible: {modes}")





class H5Manager:

    defaultmode = 'a'
    H5FILES = _weakref.WeakValueDictionary()

    __slots__ = (
        'filepath', 'omode',
        'isopener', 'master', 'lockcode', 'h5file',
        )

    def __init__(self,
            name, path='.', /, *,
            mode=None, purge=False, ext='h5'
            ):
        path = _os.path.abspath(_os.path.expanduser(path))
        filepath = self.filepath = f"{_os.path.join(path, name)}.{ext}"
        if purge:
            purge_address(filepath)
        self.mode = self.defaultmode if mode is None else mode

    @_mpi_wrap
    def _open_h5file(self):
        if hasattr(self, 'h5file'):
            return False
        filepath = self.filepath
        h5files = self.H5FILES
        if filepath in h5files:
            h5file = h5files[filepath]
            compare_modes(h5file.mode, self.mode)
            return False
        self.h5file = h5files[filepath] = H5File(filepath, self.mode)
        return True

    def __enter__(self):
        lockcode = _reseed.rstr(16)
        while True:
            try:
                self.master = lock(self.filepath, lockcode)
                break
            except AccessForbidden:
                _reseed.rsleep(0.1, 0.2) # potentially not parallelsafe
        self.lockcode = lockcode
        if hasattr(self, 'h5file'):
            return False
        self.isopener = self._open_h5file()
        return self.h5file

    @_mpi_wrap
    def _close_h5file(self):
        if self.isopener:
            self.h5file.flush()
            self.h5file.close()
            del self.h5file
            del self.H5FILES[self.filepath]

    def __exit__(self, *args):
        self._close_h5file()
        if self.master:
            release(self.filepath, self.lockcode)
        del self.lockcode


###############################################################################
###############################################################################


# def h5filewrap(func):
#     @_wraps(func)
#     def wrapper(name, path='.', /, *args, mode='a', purge=False, **kwargs):
#         with H5Manager(name, path, mode=mode, purge=purge) as h5file:
#             return func(h5file, *args, **kwargs)
#     return wrapper


# def h5filewrapmeth(func):
#     @_wraps(func)
#     def wrapper(self, *args, **kwargs):
#         with self as h5file:
#             return func(self, h5file, *args, **kwargs)
#     return wrapper


# def local_import(filepath):
#     modname = os.path.basename(filepath)
#     spec = importlib.util.spec_from_file_location(
#         modname,
#         filepath,
#         )
#     module = importlib.util.module_from_spec(spec)
#     sys.modules[modname] = module
#     spec.loader.exec_module(module)
#     return module


# class ToOpen:
#     def __init__(self, filepath):
#         self.filepath = filepath
#     @_mpi_wrap
#     def __call__(self):
#         with open(self.filepath) as file:
#             return file.read()


# @_mpi_wrap
# def write_file(filename, content, mode='w'):
#     with open(filename, mode) as file:
#         file.write(content)


# @_mpi_wrap
# def remove_file(filename):
#     if _os.path.exists(filename):
#         _os.remove(filename)


# class TempFile:

#     def __init__(self, content='', path = None, extension='txt', mode='w'):
#         if path is None:
#             global PYTEMP
#             path = PYTEMP
#         mpi.dowrap(_os.makedirs)(path, exist_ok = True)
#         tempfilename = tempname() + '.' + extension
#         self.filePath = _os.path.abspath(_os.path.join(path, tempfilename))
#         self.content, self.mode = content, mode

#     def __enter__(self):
#         write_file(self.filePath, self.content, self.mode)
#         _time.sleep(0.1) # needed to make Windows work!!!
#         return self.filePath

#     def __exit__(self, *args):
#         remove_file(self.filePath)


# def local_import(filepath):
#     filepath = _os.path.abspath(filepath)
#     path = _os.path.dirname(filepath)
#     name = _os.path.splitext(_os.path.basename(filepath))[0]
#     if not path in _sys.path:
#         pathAdded = True
#         _sys.path.insert(0, path)
#     else:
#         pathAdded = False
#     try:
#         module = _importlib.import_module(name)
#     finally:
#         if pathAdded:
#             _sys.path.remove(path)
#     return module


# def local_import_from_str(scriptString):
#     with TempFile(
#                 scriptString,
#                 extension = 'py'
#                 ) \
#             as tempfile:
#         imported = local_import(tempfile)
#     return imported
