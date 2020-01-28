import os
import sys
import json
import shutil
import tarfile
import importlib
import traceback
import random
import subprocess
import h5py
import numpy as np
import string
import time

from functools import partial

from . import exceptions
from . import utilities
message = utilities.message
from . import mpi

from .exceptions import EverestException
class H5Error(EverestException):
    '''Something went wrong with retrieving from h5 file.'''
    pass

h5File = h5py.File

PYTEMP = '/home/jovyan/pytemp'
if mpi.rank == 0:
    os.makedirs(PYTEMP, exist_ok = True)
    if not PYTEMP in sys.path:
        sys.path.append(PYTEMP)

# h5File = partial(
#     h5py.File,
#     driver = 'mpio',
#     comm = mpi.comm
#     )

def check_file(filename, checks = 10):
    check = 0
    if mpi.rank == 0:
        while True:
            if os.path.isfile(filename):
                break
            elif check < checks:
                check += 1
                time.sleep(0.1)
            else:
                raise Exception("File check failed!")

def tempname(length = 16, extension = None):
    name = ''
    if mpi.rank == 0:
        letters = string.ascii_lowercase
        name = ''.join(random.choice(letters) for i in range(length))
    name = mpi.share(name)
    if not extension is None:
        name += '.' + extension
    name = os.path.join(PYTEMP, name)
    return name

def write_file(filename, content, mode = 'w'):
    if mpi.rank == 0:
        with open(filename, mode) as file:
            file.write(content)
    # check_file(filename)

def remove_file(filename):
    if mpi.rank == 0:
        if os.path.exists(filename):
            os.remove(filename)

def h5filewrap(func):
    def wrapper(*args, **kwargs):
        self = args[0]
        outputs = None
        if mpi.rank == 0:
            with h5py.File(self.h5filename) as h5file:
                self.h5file = h5file
                outputs = func(*args, **kwargs)
        outputs = mpi.share(outputs)
        return outputs
    return wrapper

class ToOpen:
    def __init__(self, filepath):
        self.filepath = filepath
    def __call__(self):
        filedata = ''
        if mpi.rank == 0:
            with open(self.filepath) as file:
                filedata = file.read()
        filedata = mpi.share(filedata)
        return filedata

class TempFile:

    def __init__(self, content = '', path = '', extension = 'txt', mode = 'w'):
        tempfilename = tempname() + '.' + extension
        self.path = os.path.join(path, tempfilename)
        self.path = os.path.abspath(self.path)
        self.content = content
        self.mode = mode

    def __enter__(self):
        write_file(self.path, self.content, self.mode)
        time.sleep(0.1) # needed to make Windows work!!!
        return self.path

    def __exit__(self, *args):
        mpi.comm.barrier()
        # remove_file(self.path)

def _process_h5obj(h5obj, h5file, framePath):
    if type(h5obj) is h5py.Group:
        return h5obj.name
    elif type(h5obj) is h5py.Dataset:
        return h5obj[...]
    elif type(h5obj) is h5py.AttributeManager:
        inDict, outDict = h5obj.items(), dict()
        for key, val in sorted(inDict):
            outDict[key] = _process_h5obj(val, h5file, framePath)
        return outDict
    elif type(h5obj) is h5py.Reference:
        return '_path_' + os.path.join(framePath, h5file[h5obj].name)
    else:
        return np.array(h5obj).item()

def get_from_h5(hashID, frameName, filePath, *groupNames):
    h5obj = None
    framePath = os.path.join(os.path.abspath(filePath), frameName) + '.frm'
    if mpi.rank == 0:
        with h5py.File(framePath, mode = 'r') as h5file:
            h5obj = h5file[hashID]
            for name in groupNames:
                if name == 'attrs':
                    h5obj = h5obj.attrs
                else:
                    h5obj = h5obj[name]
                    if type(h5obj) is h5py.Reference:
                        h5obj = h5file[h5obj]
            h5obj = _process_h5obj(h5obj, h5file, framePath)
    h5obj = mpi.share(h5obj)
    return h5obj

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
                extension = 'py',
                mode = 'w'
                ) \
            as tempfile:
        imported = local_import(tempfile)
    return imported

def local_import_from_h5(hashID, frameName, filePath, *groupNames):
    script = get_from_h5(hashID, frameName, filePath, *groupNames)
    with TempFile(script, extension = 'py', mode = 'w') as tempfile:
        imported = local_import(tempfile)
    return imported

# def local_import(script_bytes):
#     with TempFile(script_bytes, extension = 'py') as tempfile:
#         modname = os.path.splitext(os.path.basename(tempfile))[0]
#         exec('import ' + modname + ' as imported')
#         # imported = local_import(tempfile)
#     return imported

#
# def expose(name, outputPath = '.', archive = None, recursive = True):
#     return _FileContextManager(name, outputPath, archive, recursive)
#
# def disk_state(path):
#     path = os.path.splitext(path)[0]
#     tarpath = path + '.tar.gz'
#     diskstate = ''
#     if mpi.rank == 0:
#         isfile = os.path.isfile(tarpath)
#         isdir = os.path.isdir(path)
#         assert not (isfile and isdir)
#         if isfile:
#             diskstate = 'tar'
#         elif isdir:
#             diskstate = 'dir'
#         else:
#             diskstate = 'clean'
#     diskstate = mpi.comm.bcast(diskstate, root = 0)
#     return diskstate
#
# def save_json(jsonObj, name, path):
#     name = os.path.splitext(os.path.basename(name))[0]
#     if mpi.rank == 0:
#         jsonFilename = os.path.join(path, name + '.json')
#         with open(jsonFilename, 'w') as file:
#              json.dump(jsonObj, file)
#     # mpi.barrier()
#
# def load_json(jsonName, path = None):
#     if path is None:
#         path = os.path.dirname(jsonName)
#     jsonName = os.path.splitext(os.path.basename(jsonName))[0]
#     filename = jsonName + '.json'
#     jsonDict = {}
#     if mpi.rank == 0:
#         with open(os.path.join(path, filename)) as json_file:
#             jsonDict = json.load(json_file)
#     jsonDict = mpi.comm.bcast(jsonDict, root = 0)
#     return jsonDict
#
#
#
# def save_script(script, name = None, path = '.'):
#     if name is None:
#         name = os.path.splitext(
#             os.path.basename(
#                 script
#                 )
#             )[0]
#     if mpi.rank == 0:
#         tweakedPath = os.path.splitext(script)[0] + ".py"
#         newPath = os.path.join(path, name + ".py")
#         shutil.copyfile(tweakedPath, newPath)
#     # mpi.barrier()
#
# def load_script(scriptName, path = None):
#     if path is None:
#         path = os.path.dirname(scriptName)
#     scriptName = os.path.splitext(os.path.basename(scriptName))[0]
#     scriptPath = os.path.join(path, scriptName) + '.py'
#     scriptModule = local_import(
#         scriptPath
#         )
#     return scriptModule
#
# def expose_tar(path, recursive = False, rmtar = True, outName = None):
#
#     tarpath = path + '.tar.gz'
#     if not outName is None:
#         path = outName
#
#     if mpi.rank == 0:
#         if not os.path.isfile(tarpath):
#             raise Exception("No tar by that name found.")
#         if os.path.isdir(path):
#             raise Exception("Output dir already exists.")
#
#     message("Tar found - unarchiving...")
#     if mpi.rank == 0:
#         with tarfile.open(tarpath) as tar:
#             tar.extractall(path)
#         assert os.path.isdir(path), \
#             "Archive contained the wrong model file somehow."
#         if rmtar:
#             os.remove(tarpath)
#             assert not os.path.isfile(tarpath)
#
#     message("Unarchived.")
#
#     if recursive:
#         was_tarred = expose_sub_tars(path)
#         return was_tarred
#
# def try_expose_tar(path, **kwargs):
#     if disk_state(path) == 'tar':
#         expose_tar(path)
#         return True
#     return False
#
# def make_tar(
#         path,
#         was_tarred = [],
#         rmdir = True,
#         outName = None,
#         compression = 'gz'
#         ):
#
#     if outName is None:
#         tarpath = path + '.tar'
#         if not compression is None:
#             tarpath += '.' + compression
#
#     else:
#         tarpath = outName
#
#     if mpi.rank == 0:
#         if os.path.isfile(tarpath):
#             raise Exception("Output tar already exists.")
#         if not os.path.isdir(path):
#             raise Exception("Input dir not found.")
#
#     message("Archiving...")
#
#     if len(was_tarred) > 0:
#         un_expose_sub_tars(was_tarred)
#
#     if mpi.rank == 0:
#         mode = 'w'
#         if not compression is None:
#             mode += ':' + compression
#         with tarfile.open(tarpath, mode) as tar:
#             tar.add(path, arcname = '')
#         assert os.path.isfile(tarpath), \
#             "The archive should have been created, but it wasn't!"
#         if rmdir:
#             shutil.rmtree(path)
#             assert not os.path.isdir(path), \
#                 "The directory should have been deleted, but it's still there!"
#
#     liberate_path(tarpath)
#
#     message("Archived.")
#
# def try_make_tar(path, **kwargs):
#     if disk_state(path) == 'dir':
#         make_tar(path)
#         return True
#     return False
#
# def expose_sub_tars(path):
#     subDirs = listdir(path)
#     was_tarred = []
#     for file in subDirs:
#         filePath = os.path.join(path, file)
#         if file[-7:] == '.tar.gz':
#             dirName = os.path.splitext(
#                 os.path.splitext(
#                     file
#                     )[0]
#                 )[0]
#             dirPath = os.path.join(path, dirName)
#             expose_tar(dirPath)
#             was_tarred.append(dirPath)
#             was_tarred.extend(expose_sub_tars(dirPath))
#         elif os.path.isdir(filePath):
#             was_tarred.extend(expose_sub_tars(filePath))
#     return was_tarred
#
# def un_expose_sub_tars(was_tarred):
#     if len(was_tarred) > 0:
#         for path in was_tarred[::-1]:
#             make_tar(path)
#     else:
#         pass
#
# def make_dir(path, exist_ok = True):
#
#     assert not disk_state(path) == 'tar'
#
#     if mpi.rank == 0:
#         if not os.path.isdir(path):
#             os.makedirs(path)
#         else:
#             if not exist_ok:
#                 raise Exception("Dir already exists.")
#     liberate_path(path)
#
#     assert disk_state(path) == 'dir'
#
# def listdir(path):
#     dirs = []
#     if mpi.rank == 0:
#         dirs = os.listdir(path)
#     dirs = mpi.comm.bcast(dirs, root = 0)
#     return dirs
#
# def isfile(path):
#     boolean = False
#     if mpi.rank == 0:
#         if os.path.isfile(path):
#             boolean = True
#     boolean = mpi.comm.bcast(boolean)
#     return boolean
#
# def isdir(path):
#     boolean = False
#     if mpi.rank == 0:
#         if os.path.isdir(path):
#             boolean = True
#     boolean = mpi.comm.bcast(boolean)
#     return boolean
#
# def path_exists(path):
#     if isfile(path) or isdir(path):
#         return True
#     return False
#
# def makedirs(path, exist_ok = False):
#     if mpi.rank == 0:
#         os.makedirs(path, exist_ok = exist_ok)
#     liberate_path(path)
#
# def explore_tree(path, ignore_strs = []):
#     directories = {}
#     path = os.path.abspath(path)
#     directories['.'] = path
#     files = listdir(path)
#     for file in files:
#         ignoreFile = False
#         for ignore_str in ignore_strs:
#             if ignore_str in file:
#                 ignoreFile = True
#         if not any([ignore_str in file for ignore_str in ignore_strs]):
#             if not file[:2] == '__':
#                 filePath = os.path.join(path, file)
#                 if isfile(filePath):
#                     directories[file] = filePath
#                 elif isdir(filePath):
#                     directories[file] = explore_tree(
#                     filePath,
#                     ignore_strs
#                     )
#     return directories
#
# def make_subdirectory(parentPath, childPath):
#     subpath = os.path.join(parentPath, childPath)
#     if mpi.rank == 0:
#         os.mkdir(subpath)
#     return subpath
#
# def make_directory_tree(path, directoryStructure, exist_ok = False):
#     if mpi.rank == 0:
#         os.makedirs(path, exist_ok = exist_ok)
#     liberate_path(path)
#     for entry in directoryStructure:
#         make_subdirectory(path, entry[0])
#         make_directory_tree(os.path.join(path, entry[0]), entry[1], exist_ok = True)
#     liberate_path(path)
#
# def is_jsonable(x):
#     try:
#         json.dumps(x)
#         return True
#     except (TypeError, OverflowError):
#         return False
#
# # def save_tree(objDict, path):
#
# def load_tree(path):
#     path = os.path.abspath(path)
#     directories = explore_tree(path)
#     loaded = {}
#     for key, val in sorted(directories.items()):
#         if type(val) == dict:
#             subtree = os.path.join(path, key)
#             loaded[key] = load_tree(subtree)
#         else:
#             name, ext = os.path.splitext(key)
#             if ext == '.json':
#                 obj = load_json(name, path)
#             elif ext == '.py' or ext == '.pyc':
#                 obj = load_script(name, path)
#             else:
#                 obj = None
#             loaded[name] = obj
#     return loaded
#
# class _FileContextManager:
#
#     def __init__(
#             self,
#             name,
#             outputPath = '.',
#             archive = True,
#             recursive = True,
#             **kwargs
#             ):
#
#         self.name = name
#         self.outputPath = os.path.abspath(outputPath)
#         self.path = os.path.join(outputPath, name)
#         self.tarpath = self.path + '.tar.gz'
#         self.archive = archive
#         self.recursive = recursive
#         self._initial_diskState = disk_state(self.path)
#         self.kwargs = kwargs
#
#         _backupdir_found = False
#         while not _backupdir_found:
#             self._backupfile = os.path.join(
#                 self.outputPath,
#                 '.' + tempname() + '.tar'
#                 )
#             if mpi.rank == 0:
#                 if not os.path.isfile(self._backupfile):
#                     _backupdir_found = True
#             _backupdir_found = mpi.comm.bcast(_backupdir_found, root = 0)
#
#     def _save_backup(self):
#         if self._initial_diskState == 'clean':
#             pass
#         else:
#             if self._initial_diskState == 'dir':
#                 path = self.path
#             else:
#                 path = self.tarpath
#             if mpi.rank == 0:
#                 assert not os.path.isfile(self._backupfile)
#                 with tarfile.open(self._backupfile, 'w') as tar:
#                     tar.add(path, arcname = '')
#                 assert os.path.isfile(self._backupfile)
#
#     def _load_backup(self):
#         if self._initial_diskState == 'clean':
#             pass
#         else:
#             if mpi.rank == 0:
#                 if os.path.isfile(self.tarpath):
#                     os.remove(self.tarpath)
#                 if os.path.isdir(self.path):
#                     shutil.rmtree(self.path)
#                 assert os.path.isfile(self._backupfile)
#                 if self._initial_diskState == 'dir':
#                     extractPath = self.path
#                 else:
#                     extractPath = self.tarpath
#                 with tarfile.open(self._backupfile) as tar:
#                     tar.extractall(extractPath)
#                 if self._initial_diskState == 'dir':
#                     assert os.path.isdir(self.path)
#                 else:
#                     assert os.path.isfile(self.tarpath)
#
#     def _remove_backup(self):
#         if mpi.rank == 0:
#             if os.path.isfile(self._backupfile):
#                 os.remove(self._backupfile)
#
#     def _try_archive(self):
#         archiveConditions = [
#             (self.archive == True),
#             (self.archive is None and self.was_archived)
#             ]
#         if any(archiveConditions):
#             make_tar(self.path)
#             assert disk_state(self.path) == 'tar'
#         else:
#             assert disk_state(self.path) == 'dir'
#
#     def _liberate_paths(self):
#         liberate_path(self.path)
#
#     def __enter__(self):
#         self._save_backup()
#         diskState = self._initial_diskState
#         if diskState == 'clean':
#             make_dir(self.path, exist_ok = False)
#             was_archived = None
#         elif diskState == 'dir':
#             was_archived = False
#         elif diskState == 'tar':
#             expose_tar(self.path)
#             was_archived = True
#         if self.recursive:
#             self.subtars = expose_sub_tars(self.path)
#         self.was_archived = was_archived
#         return FileManager(self.name, self.outputPath, **self.kwargs)
#
#     def __exit__(self, *args):
#         exc_type, exc_value, tb = args
#         if exc_type is None:
#             if self.recursive:
#                 if len(self.subtars) > 0:
#                     un_expose_sub_tars(self.subtars)
#             self._try_archive()
#             self._remove_backup()
#             return True
#         else:
#             message("Failed! Reverting to backup.")
#             traceback.print_exception(exc_type, exc_value, tb)
#             self._load_backup()
#             if not self._initial_diskState == 'tar':
#                 self._try_archive()
#             self._remove_backup()
#             return False
#
# class FileManager:
#
#     def __init__(
#             self,
#             name,
#             outputPath = '.',
#             load_fmopts = True,
#             save_fmopts = True,
#             ignore_strs = [],
#             **kwargs
#             ):
#
#         self.name = name
#         self.outputPath = os.path.abspath(outputPath)
#         self.path = os.path.join(outputPath, name)
#         makedirs(self.path, exist_ok = True)
#         # self._handle_kwargs(load_fmopts, save_fmopts, **kwargs)
#         self.ignore_strs = ignore_strs
#         self._update()
#
#     # def _handle_kwargs(self, load_fmopts, save_fmopts, **kwargs):
#     #     if load_fmopts and isfile(os.path.join(self.path, '_fmopts.json')):
#     #         fmopts = self.load_json('_fmopts')
#     #     else:
#     #         fmopts = {}
#     #         fmopts['ignore_strs'] = []
#     #         fmopts.update(**kwargs)
#     #     if save_fmopts:
#     #         if isfile(os.path.join(self.path, '_fmopts.json')):
#     #             self.remove('_fmopts.json')
#     #         self.save_json(fmopts, '_fmopts')
#     #     print(fmopts)
#     #     self.__dict__.update(**fmopts)
#
#     def liberate_path(self, path = ''):
#         liberate_path(os.path.join(self.path, path))
#
#     def _get_path(self, subPath):
#         path = os.path.join(self.path, subPath)
#         make_dir(path, exist_ok = True)
#         return path
#
#     def _get_directories(self):
#         self.directories = explore_tree(
#             self.path,
#             ignore_strs = self.ignore_strs
#             )
#
#     def _update(self):
#         self._get_directories()
#         self.liberate_path()
#
#     def update(self):
#         self._update()
#
#     def mkdir(self, subPath, **kwargs):
#         if mpi.rank == 0:
#             os.mkdir(
#                 os.path.join(self.path, subPath),
#                 **kwargs
#                 )
#         self._update()
#
#     def rmdir(self, subPath, **kwargs):
#         if mpi.rank == 0:
#             os.rmdir(
#                 os.path.join(self.path, subPath),
#                 **kwargs
#                 )
#         self._update()
#
#     def makedirs(self, subPath, **kwargs):
#         if mpi.rank == 0:
#             os.makedirs(
#                 os.path.join(self.path, subPath),
#                 **kwargs
#                 )
#         self._update()
#
#     def removedirs(self, subPath, **kwargs):
#         if mpi.rank == 0:
#             os.removedirs(
#                 os.path.join(self.path, subPath),
#                 **kwargs
#                 )
#         self._update()
#
#     def rmtree(self, subPath, **kwargs):
#         if mpi.rank == 0:
#             shutil.rmtree(
#                 os.path.join(self.path, subPath),
#                 **kwargs
#                 )
#         self._update()
#
#     def copytree(self, *args, **kwargs):
#         if mpi.rank == 0:
#             shutil.copytree(
#                 *args,
#                 **kwargs
#                 )
#         self._update()
#
#     def copyfrom(self, src, subPath = '', **kwargs):
#         self.copytree(
#             src,
#             os.path.join(self.path, subPath),
#             **kwargs
#             )
#         self._update()
#
#     def copyto(self, dst, subPath = '', **kwargs):
#         self.copytree(
#             os.path.join(self.path, subPath),
#             dst,
#             **kwargs
#             )
#         self._update()
#
#     def listdir(self, subPath = ''):
#         path = os.path.join(self.path, subPath)
#         return listdir(path)
#
#     def copyfile(self, src, dst):
#         if mpi.rank == 0:
#             shutil.copyfile(
#                 os.path.join(self.path, src),
#                 os.path.join(self.path, dst)
#                 )
#         self._update()
#
#     def remove(self, src):
#         if mpi.rank == 0:
#             os.remove(
#                 os.path.join(self.path, src)
#                 )
#         self._update()
#
#     def move(self, src, dst):
#         self.copyfile(src, dst)
#         self.remove(src)
#
#     def make_directory_tree(self, structure, subPath = '', **kwargs):
#         path = os.path.join(self.path, subPath)
#         make_directory_tree(path, structure, **kwargs)
#         self._update()
#
#     # def save_tree(self, saveDict):
#     #     pass
#     #
#     # def load_tree(self):
#     #     pass
#
#     def save_json(self, object, objName, subPath = ''):
#         save_json(
#             object,
#             objName,
#             self._get_path(subPath)
#             )
#         self._update()
#
#     def load_json(self, objName, subPath = ''):
#         return load_json(
#             objName,
#             self._get_path(subPath)
#             )
#
#     def save_module(self, script, name = None, subPath = ''):
#         save_script(
#             script,
#             name,
#             self._get_path(subPath)
#             )
#         self._update()
#
#     def load_module(self, name, subPath = ''):
#         return load_script(
#             name,
#             self._get_path(subPath)
#             )
#
#     def save_vars(self, varDict, subPath = ''):
#         varsOnDisk(
#             varDict,
#             self._get_path(subPath),
#             mode = 'save'
#             )
#         self._update()
#
#     def load_vars(self, varDict, subPath = ''):
#         varsOnDisk(
#             varDict,
#             self._get_path(subPath),
#             mode = 'load'
#             )
