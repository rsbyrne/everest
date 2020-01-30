import os
import sys
import json
import shutil
import tarfile
import importlib
import traceback
import random
import subprocess
import h5py
import numpy as np
import string
import time

from functools import partial

from . import exceptions
from . import utilities
message = utilities.message
from . import mpi

from .exceptions import EverestException
class H5Error(EverestException):
    '''Something went wrong with retrieving from h5 file.'''
    pass

h5File = h5py.File

PYTEMP = '/home/jovyan/pytemp'
if mpi.rank == 0:
    os.makedirs(PYTEMP, exist_ok = True)
    if not PYTEMP in sys.path:
        sys.path.append(PYTEMP)

# h5File = partial(
#     h5py.File,
#     driver = 'mpio',
#     comm = mpi.comm
#     )

def check_file(filename, checks = 10):
    check = 0
    if mpi.rank == 0:
        while True:
            if os.path.isfile(filename):
                break
            elif check < checks:
                check += 1
                time.sleep(0.1)
            else:
                raise Exception("File check failed!")

def tempname(length = 16, extension = None):
    name = None
    if mpi.rank == 0:
        letters = string.ascii_lowercase
        name = ''.join(random.choice(letters) for i in range(length))
        assert not name is None
    name = mpi.share(name)
    if not extension is None:
        name += '.' + extension
    name = os.path.join(PYTEMP, name)
    return name

def write_file(filename, content, mode = 'w'):
    if mpi.rank == 0:
        with open(filename, mode) as file:
            file.write(content)
    # check_file(filename)

def remove_file(filename):
    if mpi.rank == 0:
        if os.path.exists(filename):
            os.remove(filename)

def h5filewrap(func):
    def wrapper(*args, **kwargs):
        self = args[0]
        output = None
        if mpi.rank == 0:
            with h5py.File(self.h5filename) as h5file:
                self.h5file = h5file
                try:
                    output = func(*args, **kwargs)
                except:
                    mpi.SubMPIError
        output = mpi.share(output)
        if isinstance(output, Exception):
            raise output
        else:
            return outputs
    return wrapper

class ToOpen:
    def __init__(self, filepath):
        self.filepath = filepath
    def __call__(self):
        filedata = ''
        if mpi.rank == 0:
            with open(self.filepath) as file:
                filedata = file.read()
        filedata = mpi.share(filedata)
        return filedata

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

def _process_h5obj(h5obj, h5file, framePath):
    if type(h5obj) is h5py.Group:
        return h5obj.name
    elif type(h5obj) is h5py.Dataset:
        return h5obj[...]
    elif type(h5obj) is h5py.AttributeManager:
        inDict, outDict = h5obj.items(), dict()
        for key, val in sorted(inDict):
            outDict[key] = _process_h5obj(val, h5file, framePath)
        return outDict
    elif type(h5obj) is h5py.Reference:
        return '_path_' + os.path.join(framePath, h5file[h5obj].name)
    else:
        array = np.array(h5obj)
        try:
            return array.item()
        except ValueError:
            return list(array)

def get_framePath(frameName, filePath):
    return os.path.join(os.path.abspath(filePath), frameName) + '.frm'

def path_exists(path):
    pathExists = False
    if mpi.rank == 0:
        pathExists = os.path.exists(path)
    return mpi.share(pathExists)

def get_from_h5(frameName, filePath, *groupNames):
    h5obj = None
    keyerror = False
    framePath = get_framePath(frameName, filePath)
    if not path_exists(framePath):
        raise OSError
    if mpi.rank == 0:
        try:
            with h5py.File(framePath, mode = 'r') as h5file:
                h5obj = h5file
                for name in groupNames:
                    if name == 'attrs':
                        h5obj = h5obj.attrs
                    else:
                        h5obj = h5obj[name]
                        if type(h5obj) is h5py.Reference:
                            h5obj = h5file[h5obj]
                h5obj = _process_h5obj(h5obj, h5file, framePath)
        except KeyError:
            keyerror = True
    keyerror = mpi.share(keyerror)
    if keyerror:
        raise KeyError
    h5obj = mpi.share(h5obj)
    return h5obj

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
