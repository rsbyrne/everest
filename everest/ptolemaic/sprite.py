###############################################################################
''''''
###############################################################################


import weakref as _weakref

from .base import PtolemaicBase as _PtolemaicBase, Primitive as _Primitive


class Sprite(_PtolemaicBase):
    '''
    The base class for all 'sprites',
    or classes whose inputs are restricted to being Primitive.
    '''

    @classmethod
    def param_checker(cls, arg):
        return isinstance(arg, _Primitive)

    def _repr(self):
        args = self.params.arguments
        return ', '.join(map('='.join, zip(args, map(str, args.values()))))


###############################################################################
###############################################################################
