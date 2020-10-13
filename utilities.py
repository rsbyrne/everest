import collections
from collections.abc import Mapping, Sequence
from collections import OrderedDict
import inspect
import numpy as np
import hashlib
import warnings

from . import mpi
message = mpi.message
from . import wordhash

from .exceptions import EverestException
class GrouperSetAttrForbidden(EverestException):
    '''
    Cannot set attributes on Grouper objects after creation. \
    Disable this lock by changing the 'lock' attribute to False.
    '''

class Grouper:
    def __init__(self, grouperDict):
        grouperDict = OrderedDict(grouperDict.copy())
        for key in grouperDict:
            if ' ' in key:
                val = grouperDict[key]
                del grouperDict[key]
                newKey = key.replace(' ', '_')
                grouperDict[newKey] = val
        self.__dict__.update(grouperDict)
        self.__dict__['grouperDict'] = grouperDict
        self.__dict__['lock'] = False
    def __getitem__(self, key):
        return self.grouperDict[key]
    def __setitem__(self, key, arg):
        setattr(self, key, arg)
    def __delitem__(self, key):
        delattr(self, key)
    def keys(self, *args, **kwargs):
        return self.grouperDict.keys(*args, **kwargs)
    def items(self, *args, **kwargs):
        return self.grouperDict.items(*args, **kwargs)
    def __setattr__(self, name, value):
        self._lockcheck(name)
        super().__setattr__(name, value)
        self.grouperDict[name] = value
    def __delattr__(self, name):
        self._lockcheck(name)
        super().__delattr__(name)
        del self.grouperDict[name]
    def _lockcheck(self, name = None):
        if hasattr(self, 'lock'):
            if self.lock and not name == 'lock':
                raise GrouperSetAttrForbidden
    def copy(self):
        return self.__class__(self.grouperDict.copy())
    def update(self, inDict):
        if isinstance(inDict, type(self)):
            inDict = inDict.grouperDict
        for key, val in sorted(inDict.items()):
            setattr(self, key, val)
    def clear(self):
        for name in self.grouperDict.keys():
            delattr(self, name)
    @property
    def hashID(self):
        return w_hash(sorted(self.grouperDict.items()))

def prettify_nbytes(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])

def is_numeric(arg):
    try:
        _ = arg + 1
        return True
    except:
        return False

def make_hash(obj):
    try:
        return get_hash(obj, make = False)
    except HashIDNotFound:
        pass
    if type(obj) is str:
        hashVal = obj
    elif hasattr(obj, 'hashID'):
        hashVal = obj.hashID
    elif hasattr(obj, 'typeHash'):
        hashVal = obj.typeHash
    elif hasattr(obj, '_hashObjects'):
        hashVal = make_hash(obj._hashObjects)
    elif isinstance(obj, Mapping):
        obj = {**obj}
        try:
            obj = OrderedDict(sorted(obj.items()))
        except TypeError:
            warnings.warn(
                "You have passed unorderable kwargs to be hashed; \
                reproducibility is not guaranteed."
                )
        hashVal = make_hash(obj.items())
    elif isinstance(obj, Sequence):
        hashList = [make_hash(subObj) for subObj in obj]
        hashVal = make_hash(str(hashList))
    elif isinstance(obj, np.generic):
        hashVal = make_hash(np.asscalar(obj))
    else:
        strObj = str(obj)
        hexID = hashlib.md5(strObj.encode()).hexdigest()
        hashVal = int(hexID, 16)
    return str(hashVal)

def w_hash(obj):
    return wordhash.get_random_phrase(
        randomseed = make_hash(obj),
        wordlength = 2,
        phraselength = 2,
        )
class HashIDNotFound(EverestException):
    pass
def get_hash(obj, make = True):
    if hasattr(obj, 'hashID'):
        hashVal = obj.hashID
    elif hasattr(obj, 'typeHash'):
        hashVal = obj.typeHash
    elif hasattr(obj, '_hashObjects'):
        hashVal = make_hash(obj._hashObjects)
    else:
        if make:
            hashVal = w_hash(obj)
        else:
            raise HashIDNotFound
    return hashVal

def _obtain_dtype(object):
    if type(object) == np.ndarray:
        dtype = object.dtype
    else:
        dtype = type(object)
    return dtype

def unique_list(listlike, func = None):
    if func is None: func = lambda e: True
    return OrderedDict(
        {e: None for e in listlike if func(e)}
        ).keys()

def flatten_dict(d, parent_key = '', sep = '_'):
    # by Imran@stackoverflow
    items = []
    parent_key = parent_key.strip(sep)
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def _unflatten_dict(host, key, val):
    splitkey = key.split('/')
    if len(splitkey) == 1:
        host[key] = val
    else:
        primekey, remkey = splitkey[0], '/'.join(splitkey[1:])
        if not primekey in host:
            host[primekey] = dict()
        process_dict(host[primekey], remkey, val)

def unflatten_dict(d):
    processed = dict()
    for key, val in sorted(d.items()):
        _unflatten_dict(processed, key, val)
    return processed
