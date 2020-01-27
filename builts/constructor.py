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
    def __init__(self, script = None, **kwargs):
        imported = disk.local_import_from_str(script)
        self.cls = imported.CLASS
        self.cls.constructor = self
        self.cls.typeHash = self.instanceHash
        super().__init__(**kwargs)
    def __call__(self, **inputs):
        obj = self.cls.__new__(self.cls, inputs)
        return obj
