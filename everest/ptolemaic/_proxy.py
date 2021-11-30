###############################################################################
''''''
###############################################################################


import abc as _abc

from everest.ptolemaic.abstract import ProxyAbstract as _ProxyAbstract
from everest.ptolemaic.essence import Essence as _Essence


class Proxy(_ProxyAbstract, metaclass=_Essence):

    @_abc.abstractmethod
    def unproxy(self, /):
        raise NotImplementedError


###############################################################################
###############################################################################
