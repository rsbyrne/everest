import numpy as np
import hashlib
from . import mpi
from . import wordhash

def message(*args):
    for arg in args:
        if mpi.rank == 0:
            print(arg)

# class SoftModule:
#
#     def __init__(
#             self,
#             _scriptBytes
#             ):
#         exec(_scriptBytes) in locals()
#         self.__dict__.update(locals())

class ToOpen:
    def __init__(self, filepath):
        self.filepath = filepath
    def __call__(self):
        filedata = ''
        if mpi.rank == 0:
            with open(self.filepath) as file:
                filedata = file.read()
        filedata = mpi.comm.bcast(filedata, root = 0)
        return filedata

def unique_list(inList):
    return list(sorted(set(inList)))

def stringify(*args):
    outStr = '{'
    if len(args) > 1:
        for inputObject in args:
            outStr += stringify(inputObject)
        typeStr = 'tup'
    else:
        inputObject = args[0]
        objType = type(inputObject)
        if objType == bytes:
            outStr += inputObject.decode()
            typeStr = 'str'
        elif objType == str:
            outStr += inputObject
            typeStr = 'str'
        elif objType == bool:
            outStr += str(inputObject)
            typeStr = 'boo'
        elif objType == int:
            outStr += str(inputObject)
            typeStr = 'int'
        elif objType == float:
            outStr += str(inputObject)
            typeStr = 'flt'
        elif objType in [list, tuple]:
            for item in inputObject:
                outStr += stringify(item)
            typeStr = 'tup'
        elif objType == set:
            for item in sorted(inputObject):
                outStr += stringify(item)
            typeStr = 'set'
        elif objType == dict:
            for key, val in sorted(inputObject.items()):
                outStr += (stringify(key))
                outStr += (stringify(val))
            typeStr = 'dct'
        elif objType == ToOpen:
            outStr += inputObject()
            typeStr = 'str'
        elif objType == np.ndarray:
            outStr += str(inputObject)
            typeStr = 'arr'
        else:
            errormsg = "Type: " + str(type(inputObject)) + " not accepted."
            raise Exception(errormsg)
    outStr += '}'
    # print(args)
    # print(outStr)
    outStr = typeStr + outStr
    return outStr

def hashstamp(inputObj):
    local_inputStr = stringify(inputObj)
    all_inputStrs = mpi.comm.allgather(local_inputStr)
    global_inputStr = ''.join(all_inputStrs)
    stamp = hashlib.md5(global_inputStr.encode()).hexdigest()
    return stamp

def wordhashstamp(inputObj):
    return wordhash.get_random_phrase(hashstamp(inputObj))
