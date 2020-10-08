#BUILTMODULE

import weakref
import os
from functools import partial
from collections import OrderedDict
import inspect

from ..utilities import Grouper, make_hash, w_hash
from .. import wordhash
from .. import disk
from ..writer import Writer
from ..reader import Reader, ClassProxy
from ..weaklist import WeakList
from .. import globevars
from ..anchor import Anchor, _namepath_process
# from ..globevars import _BUILTTAG_, _CLASSTAG_


from ..exceptions import EverestException
class BuiltException(EverestException):
    pass
class MissingMethod(BuiltException):
    pass
class MissingAttribute(BuiltException):
    pass
class MissingKwarg(BuiltException):
    pass
class NotOnDiskError(EverestException):
    '''That hashID could not be found at the provided location.'''
    pass


def load(hashID, name = None, path = '.'):
    try: name, path = _namepath_process(name, path)
    except TypeError: raise NotOnDiskError
    return Reader(name, path).load_built(hashID)

# BUFFERSIZE = 5 * 2 ** 30 # i.e. 5 GiB
# def buffersize_exceeded():
#     nbytes = 0
#     for builtID, built in sorted(Meta._prebuilts.items()):
#         nbytes += built.nbytes
#     return nbytes > BUFFERSIZE

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

def sort_inputKeys(func):
    ghostTag = globevars._GHOSTTAG_
    ghostCatTag = '(' + ghostTag + ')'
    initsource = inspect.getsource(func).split('\n')
    initsource = [line.strip() for line in initsource]
    initsource = initsource[1:initsource.index('):')]
    catsDict = OrderedDict({None: []})
    ghostCatsDict = OrderedDict({None: []})
    tag = None
    appendList = catsDict[None]
    for line in initsource:
        if line[0] == '#':
            tag = line[2:].lower()
            if tag == ghostTag:
                appendList = ghostCatsDict[None]
            elif tag.endswith(ghostCatTag):
                tag = tag[:-len(ghostCatTag)].strip()
                if not tag in ghostCatsDict:
                    ghostCatsDict[tag] = []
                appendList = ghostCatsDict[tag]
            else:
                if not tag in catsDict:
                    catsDict[tag] = []
                appendList = catsDict[tag]
        else:
            key = line.split('=')[0].strip()
            if key.startswith(ghostTag):
                assert not appendList in catsDict.values()
                key = key[len(ghostTag):]
                ghostCatsDict[None].append(key)
            appendList.append(key)
    catsDict['all'] = [i for k, sl in catsDict.items() for i in sl]
    ghostCatsDict['all'] = [i for k, sl in ghostCatsDict.items() for i in sl]
    catsDict = OrderedDict(
        [(key, tuple(val)) for key, val in catsDict.items()]
        )
    ghostCatsDict = OrderedDict(
        [(key, tuple(val)) for key, val in ghostCatsDict.items()]
        )
    return catsDict, ghostCatsDict

class Meta(type):

    _preclasses = weakref.WeakValueDictionary()

    @staticmethod
    def _type_hash(arg):
        rawHash = make_hash(arg)
        neatHash = wordhash.get_random_cityword(
            randomseed = rawHash
            )
        return neatHash

    def __new__(cls, name, bases, dic):
        outCls = super().__new__(cls, name, bases, dic)
        if hasattr(outCls, '_swapscript'):
            script = outCls._swapscript
        else:
            script = disk.ToOpen(inspect.getfile(outCls))()
        typeHash = Meta._type_hash(script)
        try:
            return cls._preclasses[typeHash]
        except KeyError:
            outCls.typeHash = typeHash
            outCls.script = script
            outCls.defaultInps = _get_default_inputs(outCls.__init__)
            try:
                outCls._sortedInputKeys, outCls._sortedGhostKeys = \
                    sort_inputKeys(outCls.__init__)
            except ValueError:
                outCls._sortedInputKeys, outCls._sortedGhostKeys = {}, {}
            outCls._custom_cls_fn()
            cls._preclasses[outCls.typeHash] = outCls
            if not hasattr(outCls, '_prebuilts'):
                outCls._prebuilts = weakref.WeakValueDictionary()
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
        obj = cls.__new__(cls, **inputs)
        try:
            return cls._prebuilts[obj.inputsHash]
        except KeyError:
            obj.__init__(**obj.inputs)
            cls._prebuilts[obj.inputsHash] = obj
            return obj

    #
    # def __reduce__(cls):
    #     args = (cls.typeHash, cls.script)
    #     kwargs = dict()
    #     print("using custom reduce")
    #     return (cls._unpickle, (args, kwargs))
    #
    # def _unpickle(cls, args, kwargs):
    #     assert not len(kwargs)
    #     print("using custom unpickle")
    #     typeHash, script = args
    #     try:
    #         return cls._preclasses[typeHash]
    #     except KeyError:
    #         return ClassProxy(script)()


class NotBuilderTuple(EverestException):
    pass


class Builder:

    def __init__(self, cls, **inputs):
        self.obj = cls.__new__(**inputs)
        self.cls = cls
        self.typeHash = self.obj.typeHash
        self.inputsHash = self.obj.inputsHash
        self.hashID = self.obj.hashID

    def __call__(self):
        obj.__init__(**obj.inputs)
        return obj

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

    @classmethod
    def _process_inputs(cls, inputs):
        for key, val in sorted(inputs.items()):
            try:
                inputs[key] = Builder.make_from_tuple(val)
            except NotBuilderTuple:
                inputs[key] = val
        return inputs
    @classmethod
    def _process_ghosts(cls, ghosts):
        for key, val in sorted(ghosts.items()):
            try:
                ghosts[key] = Builder.make_from_tuple(val)
            except NotBuilderTuple:
                ghosts[key] = val
        return ghosts
    @staticmethod
    def _inputs_hash(arg):
        rawHash = make_hash(arg)
        neatHash = wordhash.get_random_phrase(
            randomseed = rawHash
            )
        return neatHash
    @classmethod
    def _get_inputs(cls, inputs = dict()):
        allinputs = OrderedDict(cls.defaultInps)
        allinputs.update(inputs)
        ghostKeys = cls._sortedGhostKeys['all']
        inputs = OrderedDict(
            [(k, v) for k, v in allinputs.items() if not k in ghostKeys]
            )
        ghosts = OrderedDict(
            [(k, v) for k, v in allinputs.items() if k in ghostKeys]
            )
        inputs = cls._process_inputs(inputs)
        ghosts = cls._process_ghosts(ghosts)
        return inputs, ghosts

    def __new__(cls, **inputs):

        inputs, ghosts = cls._get_inputs(**inputs)
        inputsHash = cls._inputs_hash(inputs)
        obj = super().__new__(cls)
        obj.inputs = inputs
        obj.ghosts = ghosts
        obj.inputsHash = inputsHash
        obj.hashID = '/'.join(obj.typeHash, obj.inputsHash)

        obj.rootObjects = {
            cls.typeHash: {'_class_': cls}
            }
        obj.globalObjects = {
            # 'classes': {cls.typeHash: cls}
            }
        obj.localObjects = {
            'typeHash': obj.typeHash,
            'inputsHash': obj.inputsHash,
            'hashID': obj.hashID,
            'inputs': obj.inputs,
            # 'class': cls
            }

        obj._anchorManager = Anchor

        return obj

    def __init__(self, **customAttributes):

        self.localObjects.update(customAttributes)
        self.localObjects['type'] = type(self).__name__

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
        self.rootwriter.add_dict(self.rootObjects)
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
    def rootwriter(self):
        man = self._anchorManager.get_active()
        return man.rootwriter
    @property
    def rootreader(self):
        man = self._anchorManager.get_active()
        return man.rootreader
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

    def __reduce__(self):
        args = [self.hashID, self.typeHash]
        kwargs = self.inputs
        return (self._unpickle, (args, kwargs))
    @classmethod
    def _unpickle(cls, args, kwargs):
        hashID, typeHash = args
        inputs = kwargs
        try:
            return type(cls)._prebuilts[hashID]
        except KeyError:
            try:
                outCls = type(cls)._preclasses[typeHash]
            except KeyError:
                outCls = self.reader.load_class(typeHash)
            return outCls(**inputs)


from ..pyklet import Pyklet
class Loader(Pyklet):
    def __init__(self, hashID, _anchorManager = Anchor):
        self._anchorManager = _anchorManager
        self.hashID = hashID
        super().__init__(hashID, _anchorManager)
    def __call__(self):
        man = self._anchorManager.get_active()
        out = man.reader.load_built(self.hashID)
        assert out.hashID == self.hashID
        return out
