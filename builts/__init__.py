import numpy as np
import hashlib
import weakref
from functools import partial

from .. import utilities
from .. import disk
from .. import wordhash
from ..writer import Writer
from ..reader import Reader

from ..globevars import _BUILTTAG_, _CLASSTAG_

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

def load(hashID, name, path = '.', get = False):
    reader = Reader(name, path)
    try: assert hashID == reader[hashID, 'hashID']
    except KeyError: raise NotInFrameError
    except OSError: raise NotOnDiskError
    typeHash = reader[hashID, 'typeHash']
    cls = load_class(typeHash, name, path)
    inputs = reader[hashID, 'inputs', '*']
    _process_loaded_inputs(inputs, name, path)
    if get: obj = cls.get(**inputs)
    else: obj = cls.build(**inputs)
    # assert obj.hashID == hashID, \
    #     "Loaded hashID " + obj.hashID + " does not match requested " + hashID
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

def load_class(typeHash, name, path):
    reader = Reader(name, path)
    script = reader['_globals_', '_classes_', typeHash]
    outclass = disk.local_import_from_str(script).CLASS
    assert typeHash == str(outclass.typeHash)
    return outclass

def _get_inputs(cls, inputs = dict()):
    defaultInps = utilities.get_default_kwargs(cls.__init__)
    inputs = {**defaultInps, **inputs}
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
        try:
            return _get_preclass(outCls.typeHash)
        except NoPreClassError:
            _PRECLASSES[outCls.typeHash] = weakref.ref(outCls)
            return outCls
    def __call__(cls, *args, **kwargs):
        obj = cls.__new__(cls, *args, **kwargs)
        obj.__init__(**obj.inputs)
        return obj

class Built(metaclass = Meta):

    @staticmethod
    def _deep_process_inputs(inputs):
        for key, val in inputs.items():
            if type(val) is np.ndarray:
                inputs[key] = list(val)

    @staticmethod
    def _process_inputs(inputs):
        # designed to be overridden
        pass

    @classmethod
    def get(cls, **kwargs):
        obj = cls.__new__(cls, **kwargs)
        try:
            return _get_prebuilt(obj.hashID)
        except NoPreBuiltError:
            obj.__init__(**obj.inputs)
            cls._add_weakref(obj)
        return obj

    @classmethod
    def build(cls, **kwargs):
        return cls(**kwargs)

    @staticmethod
    def _add_weakref(obj):
        if not obj.hashID in _PREBUILTS:
            obj.ref = weakref.ref(obj)
            _PREBUILTS[obj.hashID] = obj.ref

    def __new__(cls, **inputs):
        inputs, inputsHash, instanceHash, hashID = _get_info(cls, inputs)
        obj = super().__new__(cls)
        obj.inputs = inputs
        obj.inputsHash = inputsHash
        obj.instanceHash = instanceHash
        obj.hashID = hashID
        obj._initialised = False
        return obj

    def __init__(self, **customAttributes):

        self.nbytes = 0

        self.anchored = False
        self._pre_anchor_fns = []
        self._post_anchor_fns = []

        self.localObjects = dict()
        self.localObjects.update(customAttributes)
        self.localObjects.update({
            'typeHash': str(self.typeHash),
            'inputsHash': str(self.inputsHash),
            'instanceHash': str(self.instanceHash),
            'hashID': self.hashID,
            'inputs': self.inputs
            })
        self.globalObjects = {
            '_classes_': {str(self.typeHash): self.script}
            }

        super().__init__()

    def __hash__(self):
        return self.instanceHash

    def _check_anchored(self):
        if not self.anchored:
            raise Exception(
                "Must be anchored first."
                )

    def anchor(self, name, path = ''):
        for fn in self._pre_anchor_fns: fn()
        self.name, self.path = name, path
        writer = Writer(name, path)
        writer.add(self.localObjects, self.hashID, _toInitialise = True)
        writer.add(self.globalObjects, '_globals_', _toInitialise = True)
        self.reader = Reader(self.name, self.path)
        for fn in self._post_anchor_fns: fn()
        self.anchored = True

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




# elif isinstance(val, Partial):
#     inputs[key] = _PARTIALTAG_ + str(val.typeHash)
#     for subKey, subVal in sorted(val.inputs.items()):
#         subKey = key + _PARTIALARGTAG_ + subKey
#         if isinstance(subVal, Placeholder):
#             subVal = _PLACEHOLDERTAG_
#         inputs[subKey] = subVal

#     @classmethod
#     def partial(cls, **inputs):
#         return Partial(cls, **inputs)
#     @classmethod
#     def pending(cls, **inputs):
#         return Pending(cls, **inputs)
#
# class Partial:
#     def __init__(self, cls, **inputs):
#         self.typeHash = cls.typeHash
#         self.inputs = inputs
#         self.cls._deep_process_inputs(self.inputs)
#         self.cls._process_inputs(self.inputs)
#         self.build = partial(self._construct, cls.build)
#         self.get = partial(self._construct, cls.get)
#     def _construct(self, constructFn, *args, **kwargs):
#         inputs = {**self.inputs}
#         args = list(args)
#         for key, val in sorted(inputs):
#             if isinstance(val, Placeholder):
#                 if key in kwargs:
#                     inputs[key] = kwargs[key]
#                     del kwargs[key]
#                 else:
#                     inputs[key] = args.pop[0]
#         if len(args): raise Exception
#         if len(kwargs): raise Exception
#         return constructFn(**inputs)
#
# class Pending:
#     def __init__(self, cls, **inputs):
#         self.cls = cls.__new__(cls, **inputs)
#         self.build = lambda: cls.build(**inputs)
#         self.get = lambda: cls.get(**inputs)
#
# class Placeholder:
#     pass
#
#     partialKeys = [key for key in inputs if inputs[key].startswith(_PARTIALTAG_)]
#     for partialKey in partialKeys:
#         modPartialKey = val.lstrip(_PARTIALTAG_)
#         partialArgKeys = [
#             key for key in inputs \
#                 if key.startswith(modPartialKey + _PARTIALARGTAG_)
#             ]
#         partialInputs = dict()
#         for key in partialArgKeys:
#             modKey = key.lstrip(partialKey).lstrip(_PARTIALARGTAG_)
#             partialInputs[modKey] = inputs.pop(key)
#         partialClass = load_class(inputs)

# _PARTIALTAG_ = '_partial_'
# _PARTIALARGTAG_ = '_partialarg_'
# _PLACEHOLDERTAG_ = '_placeholder_'
