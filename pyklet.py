import inspect
import pickle

class Pyklet:
    _TAG_ = '_pyklet_'
    def __init__(self, *args, **kwargs):
        self._source = inspect.getsource(self.__class__)
        self.args, self.kwargs = args, kwargs
    def __reduce__(self):
        self._hashObjects = (args, kwargs, self._source)
        self._pickleClass = pickle.dumps(self.__class__)
        return (self._unpickle, (args, kwargs))
    @classmethod
    def _unpickle(cls, args, kwargs):
        return cls(*args, **kwargs)

# import inspect
# import pickle
#
# from .globevars import _BUILTTAG_, _CLASSTAG_
#
# # This module is a mess due to circular references in imports -
# # must refactor to avoid this.
#
# class Pyklet:
#     _TAG_ = '_pyklet_'
#     def __init__(self, *args, **kwargs):
#         self._source = inspect.getsource(self.__class__)
#         self.args, self.kwargs = args, kwargs
#     def __reduce__(self):
#         from .builts import Built, Meta
#         args, kwargs = self.args, self.kwargs
#         man = self._get_man()
#         args = [
#             self._process_input(arg, man, Built, Meta)
#             for arg in args
#             ]
#         kwargs = {
#             self._process_input(k, man, Built, Meta): \
#             self._process_input(v, man, Built, Meta)
#                 for k, v in sorted(kwargs.items())
#             }
#         self._hashObjects = (args, kwargs, self._source)
#         self._pickleClass = pickle.dumps(self.__class__)
#         return (self._unpickle, (args, kwargs))
#     @classmethod
#     def _unpickle(cls, args, kwargs):
#         man = cls._get_man()
#         args = [
#             cls._unprocess_input(arg, man)
#             for arg in args
#             ]
#         kwargs = {
#             cls._unprocess_input(k, man): cls._unprocess_input(v, man)
#                 for k, v in sorted(kwargs.items())
#             }
#         return cls(*args, **kwargs)
#     @staticmethod
#     def _process_input(inp, man, Built, Meta):
#         if type(inp) is Meta:
#             if not man is None:
#                 man.globalwriter.add_dict({'classes': {inp.typeHash: inp}})
#             return _CLASSTAG_ + inp.typeHash
#         elif isinstance(inp, Built):
#             if not man is None:
#                 inp.touch(man.name, man.path)
#             return _BUILTTAG_ + inp.hashID
#         else:
#             return inp
#     @staticmethod
#     def _unprocess_input(inp, man):
#         if type(inp) is str:
#             if inp.startswith(_CLASSTAG_):
#                 if man is None:
#                     raise Exception
#                 return man.reader.load_class(inp)
#             elif inp.startswith(_BUILTTAG_):
#                 if man is None:
#                     raise Exception
#                 return man.reader.load_built(inp)
#         return inp
#     @classmethod
#     def _get_man(cls):
#         from .anchor import Anchor, NoActiveAnchorError
#         try:
#             man = Anchor.get_active()
#         except NoActiveAnchorError:
#             man = None
#         return man
