class EverestException(Exception):
    '''PlanetEngine exception.'''
    pass

class NotTypicalBuilt(EverestException):
    '''Must use special load method for this built.'''
    pass

class CountNotOnDiskError(EverestException):
    '''That count could not be found at the target location.'''
    pass

class InDevelopmentError(EverestException):
    pass

class NotYetImplemented(EverestException):
    '''This feature has not been implemented yet.'''

class MissingMethod(EverestException):
    '''
    The user has failed to provide an expected method \
    when inheriting from an Everest class.
    '''

class MissingAsset(EverestException):
    pass
