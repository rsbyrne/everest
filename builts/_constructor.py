from .. import disk
from . import Meta
from . import Built

class Constructor(Built):
    def __init__(
            self,
            buildScript : str = None,
            buildInputs : dict = dict(),
            **kwargs
            ):
        self.buildScript = buildScript
        self.buildInputs = buildInputs
        self.cls = disk.local_import_from_str(buildScript)
        if not type(self.cls) is Meta:
            raise TypeError
        super().__init__(
            buildScript = buildScript,
            buildHash = str(self.cls.typeHash),
            **kwargs
            )
    def construct(self, **inputs):
        inputs = {**self.buildInputs, **inputs}
        return self.cls.build(**inputs)
