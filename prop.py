from .pyklet import Pyklet
from .utilities import w_hash

class Prop(Pyklet):

    def __init__(self,
            target,
            *props
            ):

        for prop in props:
            if not type(prop) is str:
                raise TypeError

        super().__init__(target, *props)

        self.target, self.props = target, props

    def __call__(self, obj = None):

        if obj is None:
            obj = self.target
        for prop in self.props:
            obj = getattr(obj, prop)

        return obj

    def _hashID(self):
        return w_hash([self.target, *self.props])
