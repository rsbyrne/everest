from .. import disk
from . import Built

class Constructor(Built):
    @staticmethod
    def _process_inputs(inputs):
        arg = inputs['script']
        if type(arg) is str:
            script = arg
        elif type(arg) is type:
            scriptFilename = arg.__init__.__globals__['__file__']
            script = disk.ToOpen(scriptFilename)()
        else:
            raise TypeError(arg)
        inputs['script'] = arg
    def __init__(self, script = None):
        with disk.TempFile(
                    arg,
                    extension = 'py',
                    mode = 'w'
                    ) \
                as tempfile:
            imported = disk.local_import(tempfile)
        cls = imported.CLASS
        super().__init__()
    def __call__(self, **inputs):
        cls.constructor = self
        obj = cls.__new__(cls, inputs)
        return constructed
