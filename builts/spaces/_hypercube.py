from . import Space
from ..vector import Vector

class HyperCube(Space):

    global _file_

    def __init__(
            self,
            **kwargs
            ):

        super().__init__(**kwargs)

from .hypercube import __file__as _file_
