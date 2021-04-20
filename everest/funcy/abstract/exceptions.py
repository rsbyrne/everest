###############################################################################
'''Defines the parent exceptions of all funcy abstract exceptions.'''
###############################################################################

from .. import exceptions as _exceptions

NotYetImplemented = _exceptions.NotYetImplemented

class FuncyAbstractException(_exceptions.FuncyException):
    '''Parent exception of all exceptions thrown by funcy.abstract.'''

class FuncyAbstractMethodException(FuncyAbstractException):
    '''The exception raised by any abstract methods not provided.'''

###############################################################################
###############################################################################
