###############################################################################
''''''
###############################################################################


import abc as _abc

from everest.ptolemaic.aspect import Aspect as _Aspect


class Proxy(_Aspect):

    @_abc.abstractmethod
    def unproxy(self, /):
        raise NotImplementedError


def unproxy_arg(arg, /):
    return arg.unproxy() if isinstance(arg, Proxy) else arg

def unproxy_argskwargs(args, kwargs, /):
    return (
        tuple(map(unproxy_arg, args)),
        dict(zip(kwargs, map(unproxy_arg, kwargs.values()))),
        )


###############################################################################
###############################################################################
