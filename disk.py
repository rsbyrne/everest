import os
import sys
import importlib
import random
import h5py
import numpy as np
import string
import time

from .utilities import message
from . import mpi

from .exceptions import EverestException
class H5Error(EverestException):
    '''Something went wrong with retrieving from h5 file.'''
    pass

PYTEMP = '/home/jovyan/pytemp'
if not PYTEMP in sys.path: sys.path.append(PYTEMP)

h5File = h5py.File

@mpi.dowrap
def tempname(length = 16, extension = None):
    letters = string.ascii_lowercase
    random.seed(time.time())
    name = ''.join(random.choice(letters) for i in range(length))
    random.seed()
    if not extension is None:
        name += '.' + extension
    return name

@mpi.dowrap
def write_file(filePath, content, mode = 'w'):
    with open(filePath, mode) as file:
        file.write(content)
    assert os.path.exists(filePath)

@mpi.dowrap
def remove_file(filePath):
    if os.path.exists(filePath):
        os.remove(filePath)
    assert not os.path.exists(filePath)

def h5filewrap(func):
    @mpi.dowrap
    def wrapper(self, *args, **kwargs):
        with h5py.File(self.h5filename) as h5file:
            self.h5file = h5file
            output = func(self, *args, **kwargs)
        return output
    return wrapper

class ToOpen:
    def __init__(self, filepath):
        self.filepath = filepath
    @mpi.dowrap
    def __call__(self):
        with open(self.filepath) as file:
            return file.read()

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
