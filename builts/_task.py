import weakref

from ._cycler import Cycler
from ._boolean import Boolean
from ..weaklist import WeakList
from .. import mpi

from ..exceptions import EverestException
class TaskSubrunFailed(EverestException):
    pass

class Task(Boolean, Cycler):

    def __init__(
            self,
            _task_stop_metaFn = all,
            **kwargs
            ):

        self._task_stop_metaFn = _task_stop_metaFn

        self._task_initialise_fns = WeakList()
        self._task_cycler_fns = WeakList()
        self._task_stop_fns = WeakList()
        self._task_finalise_fns = WeakList()

        super().__init__(**kwargs)

        self.promptees = dict()

        # Cycler attributes:
        self._cycle_fns.append(self._task_cycleFn)

        # Boolean attributes:
        self._bool_fns.append(self._task_boolFn)

    def _task_cycleFn(self):
        for fn in self._task_initialise_fns: fn()
        while not self:
            for fn in self._task_cycler_fns: fn()
            self.prompt_promptees()
        for fn in self._task_finalise_fns: fn()

    def _task_boolFn(self):
        return self._task_stop_metaFn([fn() for fn in self._task_stop_fns])

    def add_promptee(self, obj):
        self.promptees[obj.hashID] = weakref.ref(obj)
    def remove_promptee(self, obj):
        del self.promptees[obj.hashID]
    def prompt_promptees(self):
        for hashID, ref in sorted(self.promptees.items()):
            promptee = ref()
            try: promptee()
            except: pass

    @mpi.dowrap
    def subrun(self, jobName = 'anon', cores = 1):

        self._check_anchored()

        import subprocess
        import os

        from ..disk import TempFile
        from ..globevars import _DIRECTORY_

        script = '' \
            + '''import sys\n''' \
            + '''import os\n''' \
            + '''workPath = '/home/jovyan/workspace'\n''' \
            + '''if not workPath in sys.path:\n''' \
            + '''    sys.path.append(workPath)\n''' \
            + '''from everest.builts import set_global_anchor\n''' \
            + '''set_global_anchor('{0}', '{1}')\n''' \
            + '''from everest.builts import load\n''' \
            + '''task = load('{2}')\n''' \
            + '''task()'''
        script = script.format(self.name, self.path, self.hashID)

        logs = os.path.abspath(os.path.join(self.path, 'logs'))
        os.makedirs(logs, exist_ok = True)
        outFilePath = os.path.join(logs, jobName + '.out')
        errorFilePath = os.path.join(logs, jobName + '.error')
        with open(outFilePath, 'w') as outFile:
            with open(errorFilePath, 'w') as errorFile:
                with TempFile(script, extension = 'py') as filePath:
                    try:
                        subprocess.check_call(
                            ['mpirun', '-np', str(cores), 'python', filePath],
                            stdout = outFile,
                            stderr = errorFile
                            )
                    except subprocess.CalledProcessError as e:
                        raise TaskSubrunFailed

        subprocess.call(
            ['sh', os.path.join(_DIRECTORY_, 'linux', 'cliplogs.sh'), errorFilePath]
            )
        subprocess.call(
            ['sh', os.path.join(_DIRECTORY_, 'linux', 'cliplogs.sh'), outFilePath]
            )
