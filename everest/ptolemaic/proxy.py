###############################################################################
''''''
###############################################################################


import abc as _abc

from everest.ptolemaic.abstract import ProxyAbstract as _ProxyAbstract
from everest.ptolemaic.aspect import Aspect as _Aspect


class Proxy(_Aspect, _ProxyAbstract):

    @_abc.abstractmethod
    def unproxy(self, /):
        raise NotImplementedError


###############################################################################
###############################################################################
