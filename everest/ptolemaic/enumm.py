###############################################################################
''''''
###############################################################################


import abc as _abc

from everest import ur as _ur

from . import ptolemaic as _ptolemaic
from .ousia import Ousia as _Ousia


class Enumm(_Ousia):

    @classmethod
    def _yield_mergenames(meta, /):
        yield from super()._yield_mergenames()
        yield ('__enumerators__', dict, _ptolemaic.PtolDict)

    @classmethod
    def body_handle_anno(meta, body, name, note, val, /):
        body['__enumerators__'][name] = note
        body[f'_{name}_'] = val

    def __iter__(cls, /):
        return iter(cls.enumerators)

    ### Disabling redundant methods:

    @property
    def __call__(cls, /):
        raise TypeError("Cannot manually call an Enumm type.")

    @property
    def __class_call__(cls, /):
        raise TypeError("Cannot manually call an Enumm type.")

    @property
    def __construct__(cls, /):
        raise TypeError("Cannot manually call an Enumm type.")

    @property
    def __retrieve__(cls, /):
        raise TypeError("Cannot manually call an Enumm type.")

    @property
    def __instantiate__(cls, /):
        raise TypeError("Cannot manually call an Enumm type.")


class _EnummBase_(metaclass=Enumm):

    __enumerators__ = {}
    __slots__ = ('serial', 'note', '_value_')

    ### Class setup:

    @classmethod
    def _get_signature(cls, /):
        return None

    @classmethod
    def __class_post_construct__(cls, /):
        super().__class_post_construct__()
        if cls.__enumerators__:
            cls._add_enumerators_()

    @classmethod
    def _add_enumerators_(cls, /):
        enumerators = []
        enumeratorsdict = {}
        _it = enumerate(cls.__enumerators__.items())
        for serial, (name, note) in _it:
            obj = cls._instantiate_(_ptolemaic.convert((serial, note)))
            setattr(cls, name, obj)
            setattr(obj, '_value_', getattr(cls, f"_{name}_", None))
            for key, val in zip(('serial', 'note'), obj.params):
                object.__setattr__(obj, key, val)
            cls.register_innerobj(name, obj)
            enumerators.append(obj)
            enumeratorsdict[name] = obj
        cls.enumerators = _ptolemaic.convert(enumerators)
        cls.enumeratorsdict = _ptolemaic.convert(enumeratorsdict)

    ### Representations:

    @property
    def name(self, /):
        return self.__relname__

    def _content_repr(self, /):
        return ', '.join(map(repr, self.params))

    def __repr__(self, /):
        return f"{self.rootrepr}.{self.__relname__}"

    def __class_getitem__(cls, arg: (int, str), /):
        if isinstance(arg, str):
            return cls.enumeratorsdict[arg]
        return cls.enumerators[arg]


###############################################################################
###############################################################################
