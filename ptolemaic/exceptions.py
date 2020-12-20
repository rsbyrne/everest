class PtolemaicException(Exception):
    pass

class NotYetImplemented(PtolemaicException):
    pass

class MissingAsset(PtolemaicException):
    pass

from funcy.exceptions import NullValueDetected
