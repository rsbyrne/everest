from .. import disk
from . import Built
from . import MetaBuilt
from . import utilities

class Constructor(Built):
    @staticmethod
    def _process_inputs(inputs):
        script = inputs['script']
        if type(script) is str:
            pass
        elif type(script) is MetaBuilt:
            scriptFilename = script.__init__.__globals__['__file__']
            script = disk.ToOpen(scriptFilename)()
            inputs['script'] = script
    def __init__(self, script = None, **kwargs):
        imported = disk.local_import_from_str(script)
        self.cls = imported.CLASS
        super().__init__(**kwargs)
    def __call__(self, **inputs):
        obj = self.cls(**inputs)
        return obj
