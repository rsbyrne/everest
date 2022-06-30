###############################################################################
''''''
###############################################################################


from collections import abc as _collabc
import os as _os
import ast as _ast

from everest.utilities import pretty as _pretty

from .sprite import Sprite as _Sprite
from .system import System as _System


class ScreedFileException(ValueError):

    ...


class Screed(metaclass=_Sprite):

    __slots__ = ('annotations',)

    __content__: str = None
    __chapters__: dict = {}

    @classmethod
    def _from_file_raw(cls, name: str, /, path: str = ''):
        filename = _os.path.join(path, name)
        if _os.path.isfile(filename):
            if not filename.endswith('.py'):
                raise ScreedFileException(
                    f"Path must point to a Python module or package:",
                    filename,
                    )
            with open(filename, mode='r') as file:
                return file.read()
        names = _os.listdir(filename)
        try:
            names.remove('__init__.py')
        except ValueError:
            raise ScreedFileException(
                f"Path must point to a Python module or package:",
                filename,
                )
        out = {'__content__': cls._from_file_raw('__init__.py', filename)}
        for name in names:
            try:
                out[_os.path.splitext(name)[0]] = \
                    cls._from_file_raw(name, filename)
            except ScreedFileException:
                pass
        return out

    @classmethod
    def from_file(cls, name: str, /, path: str = ''):
        return cls(cls._from_file_raw(name, path))

    def to_file(self, name: str, /, path: str = ''):
        filename = _os.path.join(path, name)
        if (subs := self.__chapters__):
            _os.mkdir(filename)
            with open(_os.path.join(filename, '__init__.py'), mode='w') as file:
                file.write(self.__content__)
            for name in subs:
                getattr(self, name).to_file(name, filename)
        else:
            with open(filename + '.py', mode='w') as file:
                file.write(self.__content__)

    @classmethod
    def __class_call__(cls, /, __content__='', **__chapters__):
        if not __chapters__:
            if isinstance(__content__, cls):
                return __content__
        return super().__class_call__(__content__, **__chapters__)

    @classmethod
    def parameterise(cls, /, __content__='', **__chapters__):
        params = super().parameterise()
        if isinstance(__content__, _collabc.Mapping):
            if __chapters__:
                raise ValueError(
                    "Cannot provide subs as both mapping and kwargs."
                    )
            __chapters__ = __content__
            __content__ = __chapters__.pop('__content__', '')
        params.__content__ = str(__content__)
        params.__chapters__ = {
            key: cls(val) for key, val in __chapters__.items()
            }
        return params

    def __init__(self, /):
        parsed = _ast.parse(self.__content__)
        self.annotations = {
            ann.target.id: (ann.annotation, ann.value)
            for ann in filter(_ast.AnnAssign.__instancecheck__, parsed.body)
            }

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.rootrepr
        _pretty.pretty_argskwargs(
            ((self.__content__,), self.__chapters__),
            p, cycle, root=root
            )


class _SteleBody_:

    __slots__ = ('_stele',)

    def __init__(self, stele, /):
        self._stele = stele

    def __getitem__(self, name, /):
        try:
            return getattr(self._stele, name)
        except AttributeError as exc:
            raise KeyError from exc

    def __setitem__(self, name, val, /):
        try:
            return setattr(self._stele, name, val)
        except AttributeError as exc:
            raise KeyError from exc

    def __delitem__(self, name, /):
        try:
            return delattr(self._stele, name)
        except AttributeError as exc:
            raise KeyError from exc


class Stele(metaclass=_System):

    __screed__: Screed

    __slots__ = ('__dict__',)

    def _process_substeles(self, /):
        for name, content in self.__screed__.__chapters__.items():
            stele = self.__ptolemaic_class__.__class_alt_call__(content)
            self.register_innerobj(name, stele)
            setattr(self, name, stele)

    def _get_exec_globals(self, /):
        return {}

    def _execute(self, /):
        exec(
            self.__screed__.__content__,
            self._get_exec_globals(),
            _SteleBody_(self),
            )

    def initialise(self, /):
        self._process_substeles()
        self._execute()
        super().initialise()


###############################################################################
###############################################################################
