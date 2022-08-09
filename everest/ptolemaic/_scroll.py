###############################################################################
''''''
###############################################################################


from collections import abc as _collabc
import os as _os
import ast as _ast

from everest.utilities import pretty as _pretty

from .sprite import Sprite as _Sprite
from .system import System as _System
from . import ptolemaic as _ptolemaic


class ScreedFileException(ValueError):

    ...


class Screed(metaclass=_Sprite):

    __slots__ = ('_parsed', 'annotations')

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
    def _parameterise_(cls, /, __content__='', **__chapters__):
        params = super()._parameterise_()
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
        super().__init__()
        parsed = self._parsed = _ast.parse(self.__content__)
        self.annotations = [
            ann.target.id
            for ann in filter(_ast.AnnAssign.__instancecheck__, parsed.body)
            ]

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.rootrepr
        _pretty.pretty_argskwargs(
            ((self.__content__,), self.__chapters__),
            p, cycle, root=root
            )


class _ScrollBody_(_collabc.Mapping):

    __slots__ = ('scroll', 'scrolldict', 'protected')

    def __init__(self, scroll, /):
        self.scroll = scroll
        self.scrolldict = scroll.__dict__
        self.protected = set(dir(scroll))

    def __getitem__(self, name, /):
        return self.scrolldict[name]

    def __setitem__(self, name, val, /):
        if name in self.protected:
            raise KeyError("Cannot override protected name:", name)
        if not name.startswith('_'):
            val = _ptolemaic.convert(val)
        self.scrolldict[name] = val

    def __delitem__(self, name, /):
        del self.scrolldict[name]

    def __iter__(self, /):
        return iter(self.scrolldict)

    def __len__(self, /):
        return len(self.scrolldict)


class Scroll(metaclass=_System):

    __slots__ = ('__dict__',)

    __screed__: Screed
    __inject__: KWARGS

    @classmethod
    def from_file(cls, name: str, /, path: str = ''):
        return cls(Screed.from_file(name, path))

    def to_file(self, name: str, /, path: str = ''):
        return self.__screed__.to_file(name, path)

    @classmethod
    def _parameterise_(cls, /, *args, **kwargs):
        params = super()._parameterise_(*args, **kwargs)
        if not isinstance(arg := params.__screed__, Screed):
            params.__screed__ = Screed(arg)
        return params

    def _subscroll_yield_injectables(self, screed, /):
        for name in screed.annotations:
            if name.startswith('_'):
                raise ValueError(
                    "Names prefixed by an underscore "
                    "are not valid for injection."
                    )
            try:
                yield name, getattr(self, name)
            except AttributeError:
                continue

    def _process_subscrolls(self, /):
        for name, screed in self.__screed__.__chapters__.items():
            scroll = self.__ptolemaic_class__.__class_alt_call__(
                screed, **dict(self._subscroll_yield_injectables(screed))
                )
            self._register_innerobj(name, scroll)
            setattr(self, name, scroll)

    def _get_exec_globals(self, /):
        return {}

    def _execute(self, /):
        exec(
            self.__screed__.__content__,
            self._get_exec_globals(),
            _ScrollBody_(self),
            )

    def __initialise__(self, /):
        self.__dict__.update(self.__inject__)
        self._execute()
        self._process_subscrolls()
        super().__initialise__()


###############################################################################
###############################################################################
