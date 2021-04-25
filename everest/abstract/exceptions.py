###############################################################################
'''Defines the parent exceptions of all funcy abstract exceptions.'''
###############################################################################

from ..exceptions import EverestException, NotYetImplemented

class FuncyAbstractException(EverestException):
    '''Parent exception of all exceptions thrown by abstract.'''

class FuncyAbstractMethodException(FuncyAbstractException):
    '''The exception raised by any abstract methods not provided.'''

###############################################################################
###############################################################################
