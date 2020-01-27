from .. import disk
from . import load
from . import Built
from . import MetaBuilt
from . import mpi

class Constructor(Built):
    @staticmethod
    def _process_inputs(inputs):
        mpi.message("Processing constructor inputs...")
        script = inputs['script']
        if type(script) is str:
            pass
        elif type(script) is MetaBuilt:
            scriptFilename = script.__init__.__globals__['__file__']
            script = disk.ToOpen(scriptFilename)()
        else:
            raise TypeError(script, type(script))
        inputs['script'] = script
        mpi.message("Constructor inputs processed.")
    def __init__(self, script = None, **kwargs):
        mpi.message("Initialising constructor...")
        imported = disk.local_import_from_str(script)
        self.cls = imported.CLASS
        self.cls.constructor = self
        self.cls.typeHash = self.instanceHash
        super().__init__(**kwargs)
        mpi.message("Constructor initialised.")
    def __call__(self, **inputs):
        mpi.message("Constructing from constructor...")
        obj = self.cls.__new__(self.cls, inputs)
        # obj = self.cls(**inputs)
        mpi.message("Constructed from constructor.")
        return obj
