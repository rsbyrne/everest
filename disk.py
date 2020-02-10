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

PYTEMP = '/home/jovyan/pytemp'
if not PYTEMP in sys.path: sys.path.append(PYTEMP)

class RandomSeeder:
    def __init__(self, seed):
        self.seed = seed
    def __enter__(self):
        random.seed(seed)
    def __exit__(self, *args):
        random.seed()

PRIMEFREQSEED = mpi.share(random.random())

def gen_primes():
    """ Generate an infinite sequence of prime numbers."""
    D = {}
    q = 2
    while True:
        if q not in D:
            yield q
            D[q * q] = [q]
        else:
            for p in D[q]:
                D.setdefault(p + q, []).append(p)
            del D[q]
        q += 1

primenos = []
for i in gen_primes():
    if 100 < i < 1000:
        primenos.append(i)
    else:
        break

def get_prime_freq():
    # expects @mpi.dowrap
    with RandomSeeder(PRIMEFREQSEED):
        return random.choice(primenos)
def millinow():
    # expects @mpi.dowrap
    timenow = 0
    timenow = round(time.time() * 1e3)
    return timenow
def prime_window():
    # expects @mpi.dowrap
    while True:
        if millinow() % get_prime_freq() == 0:
            break
        else:
            time.sleep(random.random() / 1000.)

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
        with H5Access(self.h5filename) as h5file:
            return func(self, *args, **kwargs)
    return wrapper

class H5Access:
    def __init__(h5filename):
        self.h5filename = h5filename
    def __enter__(self):
        try:
            while True:
                prime_window()
                with h5py.File(self.h5filename, mode = 'r') as h5file:
                    if h5file.attrs['_BUSY_']:
                        print("File busy - waiting...")
                    else:
                        print("File available - accessing.")
                        break
        except OSError:
            pass
        self.h5file = h5py.File(self.h5filename)
        self.h5file.attrs['_BUSY_'] = True
        return self.h5file
    def __exit__(self, exc_type, exc_val, traceback):
        self.h5file.attrs['_BUSY_'] = False
        self.h5file.close()

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
