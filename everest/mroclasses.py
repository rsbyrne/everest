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
    def get_antipnames(cls, ACls):
        filt = filter(cls.isantip, ACls.__dict__.values())
        names = [att.name for att in filt]
        for Base in ACls.__bases__:
            names.extend(cls.get_antipnames(Base))
        return sorted(set(names))
    @classmethod
    def process_antips(cls, ACls):
        names = cls.get_antipnames(ACls)
        for name in names:
            for B in ACls.__mro__:
                try:
                    att = getattr(B, name)
                    if not cls.isantip(att):
                        setattr(ACls, name, att)
                        break
                except AttributeError:
                    continue
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
            b for b in cls.__bases__ if name in b.__dict__
            )
        )
    new = cls.__dict__[name] if name in cls.__dict__ else None
    if not inheritees:
        if new is not None:
            return new
        return NotImplemented
    else:
        if new is None:
            if len(inheritees) == 1:
                return inheritees[0]
        else:
            inheritees = (new, *inheritees)
        return type(name, inheritees, {})

def process_mroclass(cls, name):
    mroclass = merge_mroclass(cls, name)
    if mroclass is NotImplemented:
        return
    setattr(cls, name, mroclass)
    if issubclass(mroclass, Overclass):
        overname = cls.__name__ + '_' + name
        print(overname)
        overclass = type(overname, (mroclass, cls), {}, overclass = True)
        setattr(cls, overname, overclass)

def update_mroclasses(cls):
    for name in cls.mroclasses:
        process_mroclass(cls, name)

def process_mroclasses(cls):
    update_mroclassnames(cls)
    update_mroclasses(cls)

def mroclassable_init_subclass(cls, overclass = False, **kwargs):
    if not overclass:
        process_mroclasses(cls)
    AnticipatedMethod.process_antips(cls)
    super(cls).__init_subclass__(**kwargs)

def mroclassable(cls):
    '''Wrapper which adds mroclasses to cls.'''
    if not any(issubclass(b, MROClassable) for b in cls.__bases__):
        process_mroclasses(cls)
        cls.__init_subclass__ = classmethod(mroclassable_init_subclass)
    return cls

###############################################################################
###############################################################################
