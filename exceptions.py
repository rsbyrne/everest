class EverestException(Exception):
    '''PlanetEngine exception.'''
    pass

class NotTypicalBuilt(EverestException):
    '''Must use special load method for this built.'''
    pass

class GetFromH5Exception(EverestException):
    '''Something went wrong with retrieving from h5 file.'''
    pass

class BuiltNotCreatedYet(EverestException):
    '''That hashID does not correspond to a previously created Built.'''
    pass
