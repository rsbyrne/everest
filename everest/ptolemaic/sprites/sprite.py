###############################################################################
''''''
###############################################################################


from . import _Ptolemaic, _Primitive


class Sprite(_Ptolemaic):
    '''
    The base class for all 'sprites',
    or classes whose inputs are restricted to being Primitive.
    '''

    @classmethod
    def check_param(cls, arg):
        if isinstance(arg, _Primitive):
            return super().check_param(arg)


###############################################################################
###############################################################################
