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

from ..globevars import _BUILTTAG_, _CLASSTAG_, _ADDRESSTAG_

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

def load(hashID, name, path = '.', get = False):
    reader = Reader(name, path)
    try: assert hashID == reader[hashID, 'hashID']
    except KeyError: raise NotInFrameError
    except OSError: raise NotOnDiskError
    typeHash = reader[hashID, 'typeHash']
    cls = load_class(typeHash, name, path)
    inputs = load_inputs(hashID + '/inputs', name, path)
    if get: obj = cls.get(**inputs)
    else: obj = cls.build(**inputs)
    obj.anchor(name, path)
    return obj

def _process_loaded_inputs(inputs, name, path, **kwargs):
    for key, val in sorted(inputs.items()):
        if type(val) is str:
            if val.startswith(_BUILTTAG_):
                hashID = val[len(_BUILTTAG_):]
                inputs[key] = load(hashID, name, path, **kwargs)
            elif val.startswith(_CLASSTAG_):
                typeHash = val[len(_CLASSTAG_):]
                inputs[key] = load_class(typeHash, name, path)
            elif val.startswith(_ADDRESSTAG_):
                address = val[len(_ADDRESSTAG_):]
                inputs[key] = load_inputs(address, name, path)

def load_inputs(address, name, path):
    reader = Reader(name, path)
    splitAddr = [*address.split('/'), '*']
    if splitAddr[0] == '': splitAddr.pop(0)
    inputs = reader[tuple(splitAddr)]
    _process_loaded_inputs(inputs, name, path)
    return inputs

def load_class(typeHash, name, path):
    reader = Reader(name, path)
    script = reader['_globals_', '_classes_', typeHash]
    outclass = disk.local_import_from_str(script).CLASS
    assert typeHash == str(outclass.typeHash)
    return outclass

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

class Meta(type):
    def __new__(cls, name, bases, dic):
        outCls = super().__new__(cls, name, bases, dic)
        if hasattr(outCls, '_file_'):
            scriptPath = outCls._file_
        else:
            scriptPath = outCls.__init__.__globals__['__file__']
        outCls.script = disk.ToOpen(scriptPath)()
        outCls.typeHash = make_hash(outCls.script)
        outCls.defaultInps, outCls.kwargsOrder = \
            utilities.get_default_kwargs(outCls.__init__, return_order = True)
        outCls._custom_cls_fn()
        try:
            return _get_preclass(outCls.typeHash)
        except NoPreClassError:
            _PRECLASSES[outCls.typeHash] = weakref.ref(outCls)
            return outCls
    def __call__(cls, *args, **kwargs):
        argkwargs = dict(
            zip(cls.kwargsOrder, args[:len(cls.kwargsOrder)])
            )
        kwargs.update(argkwargs)
        obj = cls.__new__(cls, **kwargs)
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
            'typeHash': str(obj.typeHash),
            'inputsHash': str(obj.inputsHash),
            'instanceHash': str(obj.instanceHash),
            'hashID': obj.hashID,
            'inputs': obj.inputs
            }
        obj.globalObjects = {
            '_classes_': {str(obj.typeHash): obj.script}
            }

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
