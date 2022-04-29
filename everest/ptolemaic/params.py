###############################################################################
''''''
###############################################################################


from .atlantean import Kwargs as _Kwargs


class Params(_Kwargs):

    def __getattr__(self, name, /):
        try:
            return super().__getattribute__(name)
        except AttributeError as exc:
            try:
                return self[name]
            except KeyError:
                raise exc


class Param:

    __slots__ = ('name',)

    def __init__(self, name: str, /):
        super().__init__()
        self.name = name

    def __get__(self, instance, _=None):
        try:
            return instance.params[self.name]
        except KeyError:
            raise AttributeError(self.name)
        # except AttributeError:
        #     return self


###############################################################################
###############################################################################
