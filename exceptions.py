class EverestException(Exception):
    '''PlanetEngine exception.'''
    pass

class NotTypicalBuilt(EverestException):
    '''Must use special load method for this built.'''
    pass
