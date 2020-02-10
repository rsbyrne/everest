from . import Space
from ..vector import Vector

class HyperCube(Space):

    from .hypercube import __file__as _file_

    def __init__(
            self,
            **kwargs
            ):

        super().__init__(**kwargs)
