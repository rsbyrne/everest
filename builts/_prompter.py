from ..weaklist import WeakList

from . import Built
# from ._promptable import Promptable
from ..exceptions import *

class PrompterException(EverestException):
    pass
class PrompterTypeError(TypeError, PrompterException):
    pass
class PrompterRegistryError(PrompterException):
    pass

class Promptees:
    def __init__(self):
        self.promptees = WeakList()
    def add(self, arg, silent = False):
        # if not isinstance(arg, Promptable):
        #     raise PrompterTypeError
        if arg in self.promptees:
            if not silent:
                raise PrompterRegistryError
        else:
            self.promptees.append(arg)
    def remove(self, arg, silent = False):
        if not arg in self.promptees:
            if not silent:
                raise PrompterRegistryError
        else:
            self.promptees.remove(arg)
    def prompt(self):
        for promptee in self.promptees:
            promptee.prompt()
    def __repr__(self):
        return str(self.promptees)

class Prompter(Built):

    def __init__(self,
            **kwargs
            ):

        self.promptees = Promptees()

        super().__init__(**kwargs)
