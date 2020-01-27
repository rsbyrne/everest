from .. import disk
from . import load
from . import Built
from . import MetaBuilt

class Constructor(Built):
    @staticmethod
    def _process_inputs(inputs):
        script = inputs['script']
        if type(script) is str:
            pass
        elif type(script) is MetaBuilt:
            scriptFilename = script.__init__.__globals__['__file__']
            script = disk.ToOpen(scriptFilename)()
        else:
            raise TypeError(script, type(script))
        inputs['script'] = script
    def __init__(self, script = None):
        with disk.TempFile(
                    script,
                    extension = 'py',
                    mode = 'w'
                    ) \
                as tempfile:
            imported = disk.local_import(tempfile)
        self.cls = imported.CLASS
        self.cls.constructor = self
        self.cls.typeHash = self.instanceHash
        super().__init__()
    def __call__(self, **inputs):
        obj = self.cls.__new__(self.cls, inputs)
        return obj
