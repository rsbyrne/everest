import numpy as np
import hashlib
import weakref
import os
from functools import partial
from collections.abc import Mapping

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

NAME = None
PATH = None
GLOBALANCHOR = False
def set_global_anchor(name, path):
    global GLOBALANCHOR, NAME, PATH
    NAME = name
    PATH = os.path.abspath(path)
    GLOBALANCHOR = True
def release_global_anchor():
    global GLOBALANCHOR, NAME, PATH
    NAME = None
    PATH = None
    GLOBALANCHOR = False
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

def load(hashID, name = None, path = '.', get = False):
    name, path = _load_namepath_process(name, path)
    reader = Reader(name, path)
    try: assert hashID == reader[hashID, 'hashID']
    except KeyError: raise NotInFrameError
    except OSError: raise NotOnDiskError
    cls = reader[hashID, 'class']
    inputs = reader[hashID, 'inputs']
    if get: obj = cls.get(**inputs)
    else: obj = cls.build(**inputs)
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

_PRECLASSES = dict()
def _get_preclass(typeHash):
    try:
        outclass = _PRECLASSES[typeHash]
        assert not outclass is None
        return outclass
    except AssertionError:
        del _PRECLASSES[typeHash]
    except KeyError:
        pass
    finally:
        raise NoPreClassError

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
    for key, val in parameters.items():
        if len(str(val)) >= 1:
            if str(val)[0] == '*':
                del out[key] # removes *args, **kwargs
    out = OrderedDict(out)
    return out

class Meta(type):
    def __new__(cls, name, bases, dic):
        outCls = super().__new__(cls, name, bases, dic)
        if hasattr(outCls, '_file_'):
            scriptPath = outCls._file_
        else:
            scriptPath = outCls.__init__.__globals__['__file__']
        outCls.script = disk.ToOpen(scriptPath)()
        outCls.typeHash = make_hash(outCls.script)
        outCls.defaultInps =_get_default_inputs(outCls.__init__)
        outCls._custom_cls_fn()
        try:
            return _get_preclass(outCls.typeHash)
        except NoPreClassError:
            _PRECLASSES[outCls.typeHash] = weakref.ref(outCls)
            return outCls
    def __call__(cls, *args, **kwargs):
        inputs = cls.defaultInps.copy()
        inputs.update(kwargs)
        for arg, key in zip(args, list(inputs)[:len(args)]):
            inputs[key] = arg
        obj = cls.__new__(cls, **inputs)
        obj.__init__(**obj.inputs)
        if obj._initAnchor:
            if GLOBALANCHOR: obj.anchor()
            else: obj.anchor(obj.name, obj.path)
        return obj

class Built(metaclass = Meta):

    @classmethod
    def _custom_cls_fn(cls):
        pass

    @staticmethod
    def _deep_process_inputs(inputs):
        pass
        # for key, val in inputs.items():
        #     if type(val) is np.ndarray:
        #         inputs[key] = val.tolist()

    @staticmethod
    def _process_inputs(inputs):
        # designed to be overridden
        pass

    # @staticmethod
    # def _process_args_kwargs(*args, **kwargs, defaults):
    #     outDict = dict()

    @classmethod
    def get(cls, *args, **kwargs):
        obj = cls.__new__(cls, **kwargs)
        try:
            return _get_prebuilt(obj.hashID)
        except NoPreBuiltError:
            obj.__init__(**obj.inputs)
            cls._add_weakref(obj)
        return obj

    @classmethod
    def build(cls, *args, **kwargs):
        return cls(*args, **kwargs)

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

        global GLOBALANCHOR, NAME, PATH
        if GLOBALANCHOR:
            obj._initAnchor = True
        else:
            if name is None:
                obj._initAnchor = False
            else:
                if path is None: raise Exception
                obj._initAnchor = True
                obj.name, obj.path = name, path

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
        global GLOBALANCHOR, NAME, PATH
        if GLOBALANCHOR:
            if not name is None and path is None:
                raise Exception("Global anchor has been set!")
            else:
                self._anchor(NAME, PATH)
        else:
            self._anchor(name, path)

    def _anchor(self, name, path):
        mpi.comm.barrier()
        for fn in self._pre_anchor_fns: fn()
        self.name, self.path = name, path
        self.writer = Writer(name, path)
        self.writer.add(self.localObjects, self.hashID)
        self.writer.add(self.globalObjects, '_globals_')
        self.reader = Reader(self.name, self.path)
        for fn in self._post_anchor_fns: fn()
        self.anchored = True
        mpi.comm.barrier()

    def _coanchored(self, coBuilt):
        if hasattr(self, 'h5filename') and hasattr(coBuilt, 'h5filename'):
            return self.writer.h5filename == coBuilt.writer.h5filename
        else:
            return False

    def coanchor(self, coBuilt):
        if not coBuilt.anchored:
            raise Exception("Trying to coanchor to unanchored built!")
        if not self._coanchored(coBuilt):
            self.anchor(coBuilt.frameID, coBuilt.path)
