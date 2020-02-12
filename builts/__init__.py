#BUILTMODULE

import numpy as np
import hashlib
import weakref
import os
from functools import partial
from collections.abc import Mapping
import inspect

from .. import mpi

from .. import utilities
from .. import disk
from .. import wordhash
from ..writer import Writer
from ..reader import Reader
from ..weaklist import WeakList

from ..exceptions import EverestException
class NoPreBuiltError(EverestException):
    '''That hashID does not correspond to a previously created Built.'''
    pass
class NotOnDiskError(EverestException):
    '''That hashID could not be found at the provided location.'''
    pass
class NotInFrameError(EverestException):
    '''No frame by that name could be found.'''
    pass
class BuiltNotFoundError(EverestException):
    '''A Built with those parameters could not be found.'''
    pass
class NoPreClassError(EverestException):
    '''That typeHash is not associated with a class on file yet.'''
    pass
class PlaceholderError(EverestException):
    '''A placeholder has been set which is yet to be fulfilled!'''
    pass
class NotYetAnchoredError(EverestException):
    pass
class GlobalAnchorRequired(EverestException):
    pass

GLOBALREADER, GLOBALWRITER = None, None
NAME, PATH = None, None
GLOBALANCHOR = False
def set_global_anchor(name, path, purge = False):
    global GLOBALANCHOR, NAME, PATH, GLOBALREADER, GLOBALWRITER
    NAME, PATH = name, os.path.abspath(path)
    fullPath = os.path.join(PATH, NAME + '.frm')
    if purge:
        if mpi.rank == 0:
            if os.path.exists(fullPath):
                os.remove(fullPath)
            if os.path.exists(fullPath + '.busy'):
                os.remove(fullPath + '.busy')
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

def _load_namepath_process(name, path):
    global GLOBALANCHOR, NAME, PATH
    if GLOBALANCHOR:
        if not name is None and path is None:
            raise Exception("Global anchor has been set!")
        name, path = NAME, PATH
    else:
        if (name is None) or (path is None):
            raise TypeError
    return name, path

def load(hashID, name = None, path = '.'):
    name, path = _load_namepath_process(name, path)
    reader = Reader(name, path)
    try: assert hashID == reader(hashID, 'hashID'), \
        "Loaded hashID does not match derived hashID!"
    except KeyError: raise NotInFrameError
    except OSError: raise NotOnDiskError
    cls = reader(hashID, 'class')
    inputs = reader(hashID, 'inputs')
    obj = cls(**inputs)
    obj.anchor(name, path)
    return obj

def _get_inputs(cls, inputs = dict()):
    inputs = {**cls.defaultInps, **inputs}
    cls._deep_process_inputs(inputs)
    cls._process_inputs(inputs)
    return inputs

def _get_hashes(cls, inputs):
    inputsHash = make_hash(inputs)
    instanceHash = make_hash((cls.typeHash, inputsHash))
    hashID = wordhash.get_random_phrase(instanceHash)
    return inputsHash, instanceHash, hashID

def _get_info(cls, inputs = dict()):
    inputs = _get_inputs(cls, inputs)
    inputsHash, instanceHash, hashID = _get_hashes(cls, inputs)
    return inputs, inputsHash, instanceHash, hashID

def make_hash(obj):
    if hasattr(obj, 'instanceHash'):
        hashVal = obj.instanceHash
    elif hasattr(obj, 'typeHash'):
        hashVal = obj.typeHash
    elif type(obj) is dict:
        hashVal = make_hash(sorted(obj.items()))
    elif type(obj) is list or type(obj) is tuple:
        hashList = [make_hash(subObj) for subObj in obj]
        hashVal = make_hash(str(hashList))
    elif isinstance(obj, np.generic):
        hashVal = make_hash(np.asscalar(obj))
    else:
        strObj = str(obj)
        hexID = hashlib.md5(strObj.encode()).hexdigest()
        hashVal = int(hexID, 16)
    return hashVal

_PREBUILTS = dict()
def _get_prebuilt(hashID):
    if not type(hashID) is str:
        raise TypeError(hashID, "is not type 'str'")
    try:
        gotbuilt = _PREBUILTS[hashID]()
    except KeyError:
        raise NoPreBuiltError
    if isinstance(gotbuilt, Built):
        return gotbuilt
    else:
        del _PREBUILTS[hashID]
        raise NoPreBuiltError

BUFFERSIZE = 2 ** 30
def buffersize_exceeded():
    nbytes = 0
    for builtID, builtRef in sorted(_PREBUILTS.items()):
        built = builtRef()
        if not built is None:
            nbytes += built.nbytes
    return nbytes > BUFFERSIZE

def _get_default_inputs(func):
    import inspect
    from collections import OrderedDict
    parameters = inspect.signature(func).parameters
    out = parameters.copy()
    if 'self' in out: del out['self']
    for key, val in out.items():
        default = val.default
        if default is inspect.Parameter.empty:
            default = None
        out[key] = default
    argi = 0
    for key, val in parameters.items():
        if str(val)[:1] == '*':
            del out[key]
        # elif str(val)[:1] == '*':
        #     del out[key]
        #     out['arg' + str(argi)] = val
        #     argi += 1
    out = OrderedDict(out)
    return out

# _PRECLASSES = dict()
# def _get_preclass(typeHash):
#     try:
#         outclass = _PRECLASSES[typeHash]
#         assert not outclass is None
#         return outclass
#     except AssertionError:
#         del _PRECLASSES[typeHash]
#     except KeyError:
#         pass
#     finally:
#         raise NoPreClassError

class Meta(type):
    def __new__(cls, name, bases, dic):
        outCls = super().__new__(cls, name, bases, dic)
        if hasattr(outCls, 'script'):
            outCls.mobile = True
            if outCls.script.startswith('_script_'):
                outCls.script = outCls.script[len('_script_'):]
            else:
                outCls.script = disk.ToOpen(outCls.script)()
            outCls.typeHash = make_hash(outCls.script)
            # try:
            #     return _get_preclass(outCls.typeHash)
            # except NoPreClassError:
            #     _PRECLASSES[outCls.typeHash] = weakref.ref(outCls)
        else:
            outCls.mobile = False
        outCls.defaultInps =_get_default_inputs(outCls.__init__)
        outCls._custom_cls_fn()
        return outCls

    @staticmethod
    def _align_inputs(cls, *args, **kwargs):
        inputs = cls.defaultInps.copy()
        inputs.update(kwargs)
        for arg, key in zip(args, list(inputs)[:len(args)]):
            inputs[key] = arg
        return inputs

    def __call__(cls, *args, **kwargs):
        inputs = Meta._align_inputs(cls, *args, **kwargs)
        obj = cls.build(**inputs)
        if (not obj.name is None) and (not obj.path is None):
            obj.anchor(obj.name, obj.path)
        return obj

class Built(metaclass = Meta):

    @classmethod
    def _custom_cls_fn(cls):
        # designed to be overridden
        pass

    @staticmethod
    def _deep_process_inputs(inputs):
        pass

    @staticmethod
    def _process_inputs(inputs):
        # designed to be overridden
        pass

    @classmethod
    def build(cls, **inputs):
        obj = cls.__new__(cls, **inputs)
        try:
            obj = _get_prebuilt(obj.hashID)
        except NoPreBuiltError:
            obj.__init__(**obj.inputs)
            cls._add_weakref(obj)
        return obj

    @staticmethod
    def _add_weakref(obj):
        if not obj.hashID in _PREBUILTS:
            obj.ref = weakref.ref(obj)
            _PREBUILTS[obj.hashID] = obj.ref

    def __new__(cls, name = None, path = None, **inputs):

        inputs, inputsHash, instanceHash, hashID = \
            _get_info(cls, inputs)
        obj = super().__new__(cls)
        obj.inputs = inputs
        obj.inputsHash = inputsHash
        obj.instanceHash = instanceHash
        obj.hashID = hashID
        obj._initialised = False

        obj.localObjects = {
            'typeHash': obj.typeHash,
            'inputsHash': obj.inputsHash,
            'instanceHash': obj.instanceHash,
            'hashID': obj.hashID,
            'inputs': obj.inputs,
            'class': cls
            }

        obj.globalObjects = {}

        obj.name, obj.path = name, path
        global GLOBALANCHOR
        if GLOBALANCHOR:
            global NAME, PATH
            if name is None: obj.name = NAME
            if path is None: obj.path = PATH

        return obj

    def __init__(self, **customAttributes):

        self.localObjects.update(customAttributes)

        self.nbytes = 0

        self.anchored = False
        self._pre_anchor_fns = WeakList()
        self._post_anchor_fns = WeakList()

        super().__init__()

    def __hash__(self):
        return self.instanceHash

    def __reduce__(self):
        global _BUILTTAG_
        return _BUILTTAG_ + self.hashID

    def __eq__(self, arg):
        if not isinstance(arg, Built):
            raise TypeError
        return self.hashID == arg.hashID

    def __lt__(self, arg):
        if not isinstance(arg, Built):
            raise TypeError
        return self.hashID < arg.hashID

    def _check_anchored(self):
        if not self.anchored: raise NotYetAnchoredError

    def anchor(self, name = None, path = None):
        if not name is None: self.name = name
        if not path is None: self.path = os.path.abspath(path)
        self.h5filename = disk.get_framePath(self.name, self.path)
        self._anchor()

    def _anchor(self):
        name, path = self.name, self.path
        for fn in self._pre_anchor_fns: fn()
        self.writer = Writer(name, path)
        self.writer.add(self.localObjects, self.hashID)
        self.writer.add(self.globalObjects, '_globals_')
        self.reader = Reader(self.name, self.path)
        for fn in self._post_anchor_fns: fn()
        self.anchored = True

    def _coanchored(self, coBuilt):
        if hasattr(self, 'h5filename') and hasattr(coBuilt, 'h5filename'):
            return self.h5filename == coBuilt.h5filename
        else:
            return False

    def coanchor(self, coBuilt):
        if not coBuilt.anchored:
            raise Exception("Trying to coanchor to unanchored built!")
        if not self._coanchored(coBuilt):
            self.anchor(coBuilt.frameID, coBuilt.path)
