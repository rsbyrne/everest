import collections
import inspect
import numpy as np
import hashlib

from . import mpi

message = mpi.message

from .exceptions import EverestException
class GrouperSetAttrForbidden(EverestException):
    '''
    Cannot set attributes on Grouper objects after creation. \
    Disable this lock by changing the 'lock' attribute to False.
    '''

class Grouper:
    def __init__(self, grouperDict):
        self.lock = False
        self.grouperDict = grouperDict.copy()
        for key in grouperDict:
            if ' ' in key:
                val = grouperDict[key]
                del grouperDict[key]
                newKey = key.replace(' ', '_')
                grouperDict[newKey] = val
        self.grouperDict['_isgrouper'] = True
        self.__dict__.update(grouperDict)
        self.lock = True
    def __getitem__(self, key):
        return self.grouperDict[key]
    def __setitem__(self, key, arg):
        self.grouperDict[key] = arg
        self.__dict__.update(grouperDict)
    def keys(self, *args, **kwargs):
        return self.__dict__.keys(*args, **kwargs)
    def items(self, *args, **kwargs):
        return self.__dict__.items(*args, **kwargs)
    def __setattr__(self, name, value):
        if hasattr(self, 'lock'):
            if self.lock and not name == 'lock':
                raise GrouperSetAttrForbidden
        super().__setattr__(name, value)

def make_hash(obj):
    if hasattr(obj, 'instanceHash'):
        hashVal = obj.instanceHash
    elif hasattr(obj, 'typeHash'):
        hashVal = obj.typeHash
    elif hasattr(obj, '_hashObjects'):
        hashVal = make_hash(obj._hashObjects)
    elif type(obj) is dict or isinstance(obj, Grouper):
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
    return str(hashVal)

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
