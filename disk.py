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

PYTEMP = '/home/jovyan'
if not PYTEMP in sys.path: sys.path.append(PYTEMP)

class RandomSeeder:
    def __init__(self, seed):
        self.seed = seed
    def __enter__(self):
        random.seed(self.seed)
    def __exit__(self, *args):
        random.seed()
#
# PRIMEFREQSEED = mpi.share(random.random())
#
# def gen_primes():
#     """ Generate an infinite sequence of prime numbers."""
#     D = {}
#     q = 2
#     while True:
#         if q not in D:
#             yield q
#             D[q * q] = [q]
#         else:
#             for p in D[q]:
#                 D.setdefault(p + q, []).append(p)
#             del D[q]
#         q += 1
#
# PRIMENOS = []
# for i in gen_primes():
#     if i > 30:
#         if i < 100:
#             PRIMENOS.append(i)
#         else:
#             break
#
# def get_prime_freq():
#     # expects @mpi.dowrap
#     global PRIMEFREQSEED
#     global PRIMENOS
#     with RandomSeeder(PRIMEFREQSEED):
#         PRIMEFREQSEED += random.random()
#         return random.choice(PRIMENOS)
# def millinow():
#     # expects @mpi.dowrap
#     timenow = 0
#     timenow = round(time.time() * 1e3)
#     return timenow
# def prime_window():
#     # expects @mpi.dowrap
#     while True:
#         if millinow() % get_prime_freq() == 0:
#             break
#         else:
#             time.sleep(random.random() / 100.)

@mpi.dowrap
def tempname(length = 16, extension = None):
    letters = string.ascii_lowercase
    with RandomSeeder(time.time()):
        name = ''.join(random.choice(letters) for i in range(length))
    if not extension is None:
        name += '.' + extension
    return name

@mpi.dowrap
def write_file(filePath, content, mode = 'w'):
    with open(filePath, mode) as file:
        file.write(content)
    assert os.path.exists(filePath), "File did not get written!"

@mpi.dowrap
def remove_file(filePath):
    if os.path.exists(filePath):
        os.remove(filePath)
    assert not os.path.exists(filePath), "File did not get removed!"

def h5writewrap(func):
    @mpi.dowrap
    def wrapper(self, *args, **kwargs):
        with H5WriteAccess(self.h5filename) as h5file:
            self.h5file = h5file
            return func(self, *args, **kwargs)
    return wrapper

def h5readwrap(func):
    tempreadname = tempname()
    @mpi.dowrap
    def wrapper(self, *args, **kwargs):
        nonlocal tempreadname
        with H5ReadAccess(self.h5filename, tempreadname) as h5file:
            self.h5file = h5file
            return func(self, *args, **kwargs)
    return wrapper

class SetMask:
    # expects @mpi.dowrap
    def __init__(self, maskNo):
        self.maskNo = maskNo
    def __enter__(self):
        self.prevMask = os.umask(0000)
    def __exit__(self, *args):
        ignoreMe = os.umask(self.prevMask)

def check_readers(h5filename):
    readers = [
        item for item in os.listdir(os.path.dirname(h5filename)) \
            if os.path.basename(h5filename) in item and '.read' in item
        ]
    return len(readers)

def random_sleep(base = 0., factor = 1.):
    with RandomSeeder(time.time()):
        time.sleep(random.random() * factor + base)

class H5WriteAccess:
    # expects @mpi.dowrap
    def __init__(self, h5filename):
        self.h5filename = h5filename
        self.busyname = self.h5filename + '.busy'
    def __enter__(self):
        with SetMask(0000):
            while True:
                try:
                    assert not check_readers(self.h5filename)
                    self.busyfile = open(self.busyname, mode = 'x')
                    break
                except (AssertionError, FileExistsError):
                    print("File busy! Waiting...")
                    random_sleep(0.1, 5.)
        self.h5file = h5py.File(self.h5filename, 'a', libver = 'latest')
        if not self.h5file.swmr_mode:
            self.h5file.swmr_mode = True
        return self.h5file
    def __exit__(self, exc_type, exc_val, traceback):
        self.h5file.close()
        self.busyfile.close()
        os.remove(self.busyname)

class H5ReadAccess:
    # expects @mpi.dowrap
    def __init__(self, h5filename, tempreadname):
        self.h5filename = h5filename
        self.busyname = self.h5filename + '.busy'
        self.readname = self.h5filename + tempreadname + '.read'
    def __enter__(self):
        with SetMask(0000):
            while True:
                try:
                    assert not os.path.exists(self.busyname)
                    self.readfile = open(self.readname, mode = 'x')
                    while os.path.exists(self.busyname):
                        # in the off chance the file became busy along the way!
                        random_sleep(0.1, 5.)
                    break
                except AssertionError:
                    print("File busy! Waiting...")
                    random_sleep(0.1, 5.)
        self.h5file = h5py.File(self.h5filename, 'r', libver = 'latest')
        return self.h5file
    def __exit__(self, exc_type, exc_val, traceback):
        self.h5file.close()
        self.readfile.close()
        os.remove(self.readname)

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
