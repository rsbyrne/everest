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

h5File = h5py.File

PYTEMP = '/home/jovyan/pytemp'
mpi.dowrap(os.makedirs)(PYTEMP, exist_ok = True)
if not PYTEMP in sys.path:
    sys.path.append(PYTEMP)

@mpi.dowrap
def tempname(length = 16, extension = None):
    letters = string.ascii_lowercase
    name = ''.join(random.choice(letters) for i in range(length))
    if not extension is None:
        name += '.' + extension
    name = os.path.join(PYTEMP, name)
    return name

@mpi.dowrap
def write_file(filename, content, mode = 'w'):
    with open(filename, mode) as file:
        file.write(content)

@mpi.dowrap
def remove_file(filename):
    if os.path.exists(filename):
        os.remove(filename)

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

    def __init__(self, content = '', path = '', extension = 'txt', mode = 'w'):
        tempfilename = tempname() + '.' + extension
        self.path = os.path.join(path, tempfilename)
        self.path = os.path.abspath(self.path)
        self.content = content
        self.mode = mode

    def __enter__(self):
        write_file(self.path, self.content, self.mode)
        time.sleep(0.1) # needed to make Windows work!!!
        return self.path

    def __exit__(self, *args):
        remove_file(self.path)

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
                extension = 'py',
                mode = 'w'
                ) \
            as tempfile:
        imported = local_import(tempfile)
    return imported
