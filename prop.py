from .pyklet import Pyklet
from .utilities import get_hash

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

        self.open = self.target is None

    def __call__(self, obj = None):

        if obj is None:
            obj = self.target
        for prop in self.props:
            obj = getattr(obj, prop)

        return obj

    def _hashID(self):
        targHash = get_hash(self.target)
        return '.'.join([targHash, *self.props])
