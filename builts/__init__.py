#BUILTMODULE

import weakref
import os
from functools import partial
from collections import OrderedDict
import inspect

from ..utilities import Grouper, make_hash
from .. import disk
from .. import wordhash
from ..writer import Writer
from ..reader import Reader
from ..weaklist import WeakList
from .. import globevars
from ..anchor import Anchor, _namepath_process

# from ..globevars import _BUILTTAG_, _CLASSTAG_


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


def load(hashID, name = None, path = '.'):
    try: name, path = _namepath_process(name, path)
    except TypeError: raise NotOnDiskError
    return Reader(name, path).load(hashID)

def _get_ghostInps(inputs):
    ghostInps = dict()
    ordinaryInps = dict()
    tag = globevars._GHOSTTAG_
    for key, val in sorted(inputs.items()):
        if key.startswith(tag):
            ghostInps[key[len(tag):]] = val
        else:
            ordinaryInps[key] = val
    return ordinaryInps, ghostInps

def _get_inputs(cls, inputs = dict()):
    inputs = {**cls.defaultInps, **inputs}
    inputs = cls._deep_process_inputs(inputs)
    inputs = cls._process_inputs(inputs)
    inputs, ghosts = _get_ghostInps(inputs)
    return inputs, ghosts

def _get_hashes(cls, inputs):
    inputsHash = make_hash(inputs)
    instanceHash = make_hash((cls.typeHash, inputsHash))
    hashID = wordhash.get_random_phrase(instanceHash)
    return inputsHash, instanceHash, hashID

def _get_info(cls, inputs = dict()):
    inputs, ghosts = _get_inputs(cls, inputs)
    inputsHash, instanceHash, hashID = _get_hashes(cls, inputs)
    return inputs, ghosts, inputsHash, instanceHash, hashID

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

BUFFERSIZE = 5 * 2 ** 30 # i.e. 5 GiB
def buffersize_exceeded():
    nbytes = 0
    for builtID, builtRef in sorted(_PREBUILTS.items()):
        built = builtRef()
        if not built is None:
            nbytes += built.nbytes
    return nbytes > BUFFERSIZE

def _get_default_inputs(func):
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

def sort_inputKeys(func):
    initsource = inspect.getsource(func).split('\n')
    initsource = [line.strip() for line in initsource]
    initsource = initsource[1:initsource.index('):')]
    keyDict = {None: []}
    tag = None
    for line in initsource:
        if line[0] == '#':
            tag = line[2:].lower()
            if not tag in keyDict:
                keyDict[tag] = []
        else:
            key = line.split('=')[0].strip()
            keyDict[tag].append(key)
    keyDict = {key: tuple(val) for key, val in keyDict.items()}
    return keyDict

class Meta(type):

    def __new__(cls, name, bases, dic):
        outCls = super().__new__(cls, name, bases, dic)
        if hasattr(outCls, '_swapscript'): script = outCls._swapscript
        else: script = disk.ToOpen(inspect.getfile(outCls))()
        outCls.typeHash = make_hash(script)
        outCls.script = script
        outCls.defaultInps = _get_default_inputs(outCls.__init__)
        try:
            outCls._sortedInputKeys = sort_inputKeys(outCls.__init__)
        except ValueError:
            pass
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
        return obj

#     def __getitem__(self, )

class NotBuilderTuple(EverestException):
    pass


class Builder:

    def __init__(self, cls, **inputs):
        self.obj = cls.__new__(**inputs)
        self.cls = cls
        self.hashID = self.obj.hashID
        self.typeHash = self.obj.typeHash
        self.inputsHash = self.obj.inputsHash
        self.instanceHash = self.obj.instanceHash

    def __call__(self):
        return self.cls.build(self.obj)

    @classmethod
    def make_from_tuple(cls, inp):
        if type(inp) is tuple:
            if len(inp) == 2:
                if type(inp[0]) is Meta and type(inp[1]) is dict:
                    return cls(inp[0], **inp[1])
        raise NotBuilderTuple


class Built(metaclass = Meta):

    @classmethod
    def _custom_cls_fn(cls):
        # designed to be overridden
        pass

    @staticmethod
    def _deep_process_inputs(inputs):
        processed = dict()
        for key, val in sorted(inputs.items()):
            try:
                processed[key] = Builder.make_from_tuple(val)
            except NotBuilderTuple:
                processed[key] = val
        return processed

    @staticmethod
    def _process_inputs(inputs):
        # designed to be overridden
        return inputs

    @classmethod
    def build(cls, obj = None, **inputs):
        if obj is None:
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

    def __new__(cls, **inputs):

        inputs, ghosts, inputsHash, instanceHash, hashID = \
            _get_info(cls, inputs)
        obj = super().__new__(cls)
        obj.inputs = inputs
        obj.ghosts = ghosts
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
            # 'class': cls
            }

        obj.globalObjects = {
            'classes': {cls.typeHash: cls}
            }

        obj._anchorManager = Anchor

        return obj

    def __init__(self, **customAttributes):

        self.localObjects.update(customAttributes)
        self.localObjects['type'] = type(self).__name__

        self.nbytes = 0

        self._pre_anchor_fns = WeakList()
        self._post_anchor_fns = WeakList()

        self.inputs = Grouper(self.inputs) # <- may be problematic!

        super().__init__()

    def touch(self, name = None, path = None):
        conds = [o is None for o in (name, path)]
        if any(conds) and not all(conds):
            raise ValueError
        if not any(conds):
            with Anchor(name, path) as anchor:
                self._touch()
        else:
            self._touch()
    @disk.h5filewrap
    def _touch(self):
        for fn in self._pre_anchor_fns: fn()
        self.writer.add_dict(self.localObjects)
        self.globalwriter.add_dict(self.globalObjects)
        for fn in self._post_anchor_fns: fn()
    @property
    def name(self):
        man = self._anchorManager.get_active()
        return man.name
    @property
    def path(self):
        man = self._anchorManager.get_active()
        return man.path
    @property
    def writer(self):
        return Writer(self.name, self.path, self.hashID)
    @property
    def reader(self):
        return Reader(self.name, self.path, self.hashID)
    @property
    def globalwriter(self):
        man = self._anchorManager.get_active()
        return man.globalwriter
    @property
    def globalreader(self):
        man = self._anchorManager.get_active()
        return man.globalreader
    @property
    def h5filename(self):
        man = self._anchorManager.get_active()
        return man.h5filename
    @property
    def anchored(self):
        return not self._anchorManager is None

    def __hash__(self):
        return int(self.instanceHash)

    def __eq__(self, arg):
        if not isinstance(arg, Built):
            raise TypeError
        return self.hashID == arg.hashID

    def __lt__(self, arg):
        if not isinstance(arg, Built):
            raise TypeError
        return self.hashID < arg.hashID


from ..pyklet import Pyklet
class Loader(Pyklet):
    def __init__(self, hashID, _anchorManager = Anchor):
        self._anchorManager = _anchorManager
        self.hashID = hashID
        super().__init__(hashID, _anchorManager)
    def __call__(self):
        man = self._anchorManager.get_active()
        out = man.reader.load(self.hashID)
        assert out.hashID == self.hashID
        return out
