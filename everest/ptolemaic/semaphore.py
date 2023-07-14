###############################################################################
''''''
###############################################################################


from everest.utilities import pretty as _pretty

from .enumm import Enumm as _Enumm
from .essence import Essence as _Essence
from .message import Message as _Message


class Semaphore(metaclass=_Enumm):

    class Dispatch(mroclass(_Message)):

        envelope: object
        content: object = None

        @classmethod
        def _parameterise_(cls, /, *args, **kwargs):
            params = super()._parameterise_(*args, **kwargs)
            if params.envelope not in cls.__corpus__:
                raise ValueError(params.envelope)
            return params

        def _pretty_repr_(self, p, cycle, /, root=None):
            return _pretty.pretty_call(
                self.envelope, ((self.content,), {}), p, cycle, root=root
                )

    def __call__(self, content, /):
        return self.Dispatch(self, content)


###############################################################################
###############################################################################
