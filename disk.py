import os
import sys
import shutil
import importlib
import random
import h5py
import numpy as np
import string
import time
from contextlib import contextmanager
from functools import wraps

from .utilities import message
from . import mpi

PYTEMP = '/home/jovyan'
if not PYTEMP in sys.path: sys.path.append(PYTEMP)

@mpi.dowrap
def purge_logs(path = '.'):
    try: shutil.rmtree(os.path.join(path, 'logs'))
    except FileNotFoundError: pass

class RandomSeeder:
    def __init__(self, seed):
        self.seed = seed
    def __enter__(self):
        random.seed(self.seed)
    def __exit__(self, *args):
        random.seed()

def random_sleep(base = 0., factor = 1.):
    with RandomSeeder(time.time()):
        time.sleep(random.random() * factor + base)

@mpi.dowrap
def tempname(length = 16, extension = None):
    letters = string.ascii_lowercase
    with RandomSeeder(time.time()):
        name = ''.join(random.choice(letters) for i in range(length))
    if not extension is None:
        name += '.' + extension
    return name

H5FILES = dict()

def h5filewrap(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        global H5FILES
        if self.h5filename in H5FILES:
            self.h5file = H5FILES[self.h5filename]
            out = func(self, *args, **kwargs)
        else:
            with H5Wrap(self):
                out = func(self, *args, **kwargs)
        return out
    return wrapper

class H5Wrap:
    def __init__(self, arg):
        self.lockfilename = arg.h5filename + '.lock'
        self.arg = arg
    @mpi.dowrap
    def _enter_wrap(self):
        global H5FILES
        while True:
            try:
                self.lockfile = open(self.lockfilename, 'x')
                break
            except FileExistsError:
                random_sleep(0.1, 5.)
        self.arg.h5file = h5py.File(self.arg.h5filename, 'a')
        H5FILES[self.arg.h5filename] = self.arg.h5file
    def __enter__(self):
        self._enter_wrap()
        return None
    @mpi.dowrap
    def _exit_wrap(self):
        global H5FILES
        self.arg.h5file.close()
        del self.arg.h5file
        del H5FILES[self.arg.h5filename]
        self.lockfile.close()
        os.remove(self.lockfilename)
    def __exit__(self, *args):
        self._exit_wrap()

class SetMask:
    # expects @mpi.dowrap
    def __init__(self, maskNo):
        self.maskNo = maskNo
    def __enter__(self):
        self.prevMask = os.umask(0000)
    def __exit__(self, *args):
        ignoreMe = os.umask(self.prevMask)

class ToOpen:
    def __init__(self, filepath):
        self.filepath = filepath
    @mpi.dowrap
    def __call__(self):
        with open(self.filepath) as file:
            return file.read()

@mpi.dowrap
def write_file(filename, content, mode = 'w'):
    with open(filename, mode) as file:
        file.write(content)

@mpi.dowrap
def remove_file(filename):
    if os.path.exists(filename):
        os.remove(filename)

class TempFile:

    def __init__(self, content = '', path = None, extension = 'txt', mode = 'w'):
        if path is None:
            global PYTEMP
            path = PYTEMP
        mpi.dowrap(os.makedirs)(path, exist_ok = True)
        tempfilename = tempname() + '.' + extension
        self.filePath = os.path.abspath(os.path.join(path, tempfilename))
        self.content, self.mode = content, mode

    def __enter__(self):
        write_file(self.filePath, self.content, self.mode)
        time.sleep(0.1) # needed to make Windows work!!!
        return self.filePath

    def __exit__(self, *args):
        remove_file(self.filePath)

def get_framePath(frameName, filePath):
    return os.path.join(os.path.abspath(filePath), frameName) + '.frm'

def local_import(filepath):
    modname = os.path.basename(filepath)
    spec = importlib.util.spec_from_file_location(
        modname,
        filepath,
        )
    module = importlib.util.module_from_spec(spec)
    sys.modules[modname] = module
    spec.loader.exec_module(module)
    return module

def local_import_from_str(scriptString):
    with TempFile(
                scriptString,
                extension = 'py'
                ) \
            as tempfile:
        imported = local_import(tempfile)
    return imported
