###############################################################################
''''''
###############################################################################


from everest.utilities import pretty as _pretty, caching as _caching

from .atlantean import Atlantean as _Atlantean


# class DiictMeta(_Ousia):

#     @property
#     def __call__(cls, /):
#         return cls.__new__

#     @classmethod
#     def get_basetyp(meta, /):
#         return dict


class Diict(dict, metaclass=_Atlantean):

    # @classmethod
    # def __class_call__(cls, /, *args, **kwargs):
    #     obj = cls.instantiate()
    #     dict.__init__(obj, *args, **kwargs)
    #     object.__setattr__(obj, 'freezeattr', _Switch(True))
    #     return obj

    @property
    def __setitem__(self, /):
        raise NotImplementedError

    @property
    def __delitem__(self, /):
        raise NotImplementedError

    def get_epitaph(self, /):
        ptolcls = self._ptolemaic_class__
        return ptolcls.taphonomy.callsig_epitaph(
            ptolcls, dict(self)
            )

    @property
    @_caching.soft_cache()
    def epitaph(self, /):
        return self.get_epitaph()

    @property
    def hexcode(self, /):
        return self.epitaph.hexcode

    @property
    def hashint(self, /):
        return self.epitaph.hashint

    @property
    def hashID(self, /):
        return self.epitaph.hashID

    def __repr__(self, /):
        valpairs = ', '.join(map(':'.join, zip(
            map(repr, self),
            map(repr, self.values()),
            )))
        return f"<{self._ptolemaic_class__}{{{valpairs}}}>"

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self._ptolemaic_class__.__qualname__
        _pretty.pretty_dict(self, p, cycle, root=root)

    def __hash__(self, /):
        return self.hashint

    def __eq__(self, other, /):
        return hash(self) == hash(other)

    def __lt__(self, other, /):
        return hash(self) < hash(other)

    def __gt__(self, other, /):
        return hash(self) < hash(other)


class Kwargs(Diict):

    def get_epitaph(self, /):
        ptolcls = self._ptolemaic_class__
        return ptolcls.taphonomy.callsig_epitaph(
            ptolcls, **self
            )

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self._ptolemaic_class__.__qualname__
        _pretty.pretty_kwargs(self, p, cycle, root=root)


###############################################################################
###############################################################################


    # for name in (
    #         '__setitem__', '__delitem__',
    #         'pop', 'popitem', 'clear', 'update', 'setdefault'
    #         ):
    #     exec('\n'.join((
    #         f'@property',
    #         f'def {name}(self, /):',
    #         f"    return self._content_.{name}",
    #         )))
    # del name