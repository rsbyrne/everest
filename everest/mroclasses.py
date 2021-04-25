###############################################################################
''''''
###############################################################################

from abc import ABC as _ABC

class Overclass(_ABC):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is Overclass:
            if any('_overclasstag_' in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented

def overclass(cls):
    '''Class decorator for designating an Overclass.'''
    cls._overclasstag_ = None
    return cls

class MROClassable(_ABC):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is MROClassable:
            if any('mroclasses' in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented

class AnticipatedMethod(Exception):
    '''Placeholder class for a missing method.'''
    __slots__ = 'func', 'name'
    @classmethod
    def isantip(cls, obj):
        return isinstance(obj, cls)
    @classmethod
    def update_antips(cls, acls):
        filt = filter(cls.isantip, acls.__dict__.values())
        antips = [att.name for att in filt]
        if hasattr(acls, '_anticipatedmethods_'):
            antips.extend(acls._anticipatedmethods_)
        antips = sorted(set(antips))
        acls._anticipatedmethods_ = antips
        assert all(antip in dir(acls) for antip in antips)
    @classmethod
    def process_antips(cls, acls):
        cls.update_antips(acls)
        for antip in acls._anticipatedmethods_:
            for B in acls.__mro__[1:]:
                try:
                    att = getattr(B, antip)
                    if not cls.isantip(att):
                        setattr(acls, antip, att)
                        break
                except AttributeError:
                    ...
    def __init__(self, func, /):
        self.func, self.name, self.doc = func, func.__name__, func.__doc__
        exc = f"A method called '{self.name}' is anticipated: {self.doc}"
        super().__init__(exc)
    def __call__(self, *args, **kwargs):
        raise self

def anticipatedmethod(func):
    return AnticipatedMethod(func)

def update_mroclassnames(cls):
    try:
        mroclasses = list(cls.mroclasses)
    except AttributeError:
        mroclasses = []
    for c in (c for c in cls.__bases__ if issubclass(c, MROClassable)):
        try:
            basemroclasses = c.mroclasses
            mroclasses.extend(
                name for name in basemroclasses if not name in mroclasses
                )
        except AttributeError:
            pass
    cls.mroclasses = tuple(mroclasses)

def merge_mroclass(cls, name):
    inheritees = tuple(
        getattr(c, name) for c in (
            b for b in (cls, *cls.__bases__) if name in b.__dict__
            )
        )
    if not inheritees:
        return NotImplemented
    if len(inheritees) == 1:
        mroclass = inheritees[0]
    else:
        mroclass = type(name, inheritees, {})
    if issubclass(mroclass, Overclass) and not issubclass(cls, mroclass):
        comboname = cls.__name__ + '_' + mroclass.__name__
        mroclass = type(comboname, (mroclass, cls), {})
    AnticipatedMethod.process_antips(mroclass)
    return mroclass

def update_mroclasses(cls):
    for name in cls.mroclasses:
        mroclass = merge_mroclass(cls, name)
        if mroclass is not NotImplemented:
            setattr(cls, name, mroclass)

def process_mroclasses(cls):
    update_mroclassnames(cls)
    update_mroclasses(cls)

def mroclassable_init_subclass(cls, **kwargs):
    process_mroclasses(cls)
    super(cls).__init_subclass__(**kwargs)

def mroclassable(cls):
    '''Wrapper which adds mroclasses to cls.'''
    if not any(issubclass(b, MROClassable) for b in cls.__bases__):
        process_mroclasses(cls)
        cls.__init_subclass__ = classmethod(mroclassable_init_subclass)
    return cls

###############################################################################
###############################################################################
