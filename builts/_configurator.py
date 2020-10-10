from ._applier import Applier

from . import BuiltException, MissingMethod, MissingAttribute, MissingKwarg
class ConfiguratorException(BuiltException):
    pass
class ConfiguratorMissingMethod(MissingMethod, ConfiguratorException):
    pass
class ConfiguratorMissingAttribute(MissingAttribute, ConfiguratorException):
    pass
class ConfiguratorMissingKwarg(MissingKwarg, ConfiguratorException):
    pass

class Configurator(Applier):

    def __init__(self,
            **kwargs
            ):

        super().__init__(**kwargs)
