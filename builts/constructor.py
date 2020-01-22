from .. import disk

from . import Built

class Constructor(Built):
    def __init__(self, arg):
        if type(arg) is str:
            self.script = arg
        elif type(arg) is type:
            scriptFilename = arg.__init__.__globals__['__file__']
            self.script = disk.ToOpen(scriptFilename)()
        else:
            raise TypeError(arg)
        self.inputs = {'script': self.script}
        super().__init__()
    def __call__(self, **inputs):
        with disk.TempFile(
                    self.script,
                    extension = 'py',
                    mode = 'w'
                    ) \
                as tempfile:
            imported = disk.local_import(tempfile)
            constructed = imported.build(_direct = True, **inputs)
        return constructed
