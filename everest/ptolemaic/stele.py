###############################################################################
''''''
###############################################################################


from collections import abc as _collabc
import os as _os

from everest.utilities import pretty as _pretty

from .ousia import Ousia as _Ousia


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


class SteleFileException(ValueError):

    ...


class Stele(metaclass=_Ousia):

    __slots__ = ('__content__', '__subcontents__', '__dict__')

    @classmethod
    def _from_file_raw(cls, name: str, /, path: str = ''):
        filename = _os.path.join(path, name)
        if _os.path.isfile(filename):
            if not filename.endswith('.py'):
                raise SteleFileException(
                    f"Path must point to a Python module or package:",
                    filename,
                    )
            with open(filename, mode='r') as file:
                return file.read()
        names = _os.listdir(filename)
        try:
            names.remove('__init__.py')
        except ValueError:
            raise SteleFileException(
                f"Path must point to a Python module or package:",
                filename,
                )
        out = {'__content__': cls._from_file_raw('__init__.py', filename)}
        for name in names:
            try:
                out[_os.path.splitext(name)[0]] = \
                    cls._from_file_raw(name, filename)
            except SteleFileException:
                pass
        return out

    @classmethod
    def from_file(cls, name: str, /, path: str = ''):
        return cls(cls._from_file_raw(name, path))

    def to_file(self, name: str, /, path: str = ''):
        filename = _os.path.join(path, name)
        if (subs := self.__subcontents__):
            _os.mkdir(filename)
            with open(_os.path.join(filename, '__init__.py'), mode='w') as file:
                file.write(self.__content__)
            for name in subs:
                getattr(self, name).to_file(name, filename)
        else:
            with open(filename + '.py', mode='w') as file:
                file.write(self.__content__)

    @classmethod
    def parameterise(cls, arg=None, /, **kwargs):
        params = super().parameterise()
        if arg is None:
            arg = kwargs
        elif kwargs:
            raise ValueError("Cannot pass in both arg and kwargs.")
        if isinstance(arg, str):
            content, steles = arg, {}
        else:
            steles = dict(arg)
            content = steles.pop('__content__', None)
        params.__content__, params.__subcontents__ = content, steles
        return params

    def _get_exec_globals(self, /):
        return {}

    def _execute(self, /):
        exec(self.__content__, self._get_exec_globals(), _SteleBody_(self))

    def _process_substeles(self, /):
        for name, content in self.__subcontents__.items():
            stele = self.__ptolemaic_class__.__class_alt_call__(content)
            self.register_innerobj(name, stele)
            setattr(self, name, stele)

    def initialise(self, /):
        self.__content__, self.__subcontents__ = self.params
        self._process_substeles()
        self._execute()
        super().initialise()

    def _content_repr(self, /):
        dct = dict(__content__=self.__content__, **self.__subcontents__)
        return ', '.join(f"{key}={repr(val)}" for key, val in dct.items())

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.rootrepr
        dct = dict(__content__=self.__content__, **self.__subcontents__)
        _pretty.pretty_kwargs(dct, p, cycle, root=root)


###############################################################################
###############################################################################
