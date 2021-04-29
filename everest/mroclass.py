###############################################################################
''''''
###############################################################################

from abc import ABC as _ABC

class Overclass(_ABC):
    overclasstag = 'overclasstag'
    @classmethod
    def __subclasshook__(cls, C):
        if cls is Overclass:
            if any(cls.overclasstag in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented
    def __new__(cls, ACls):
        '''Class decorator for designating an Overclass.'''
        setattr(ACls, cls.overclasstag, None)
        return ACls

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

def _mroclassable_init_subclass(ACls, ocls = False):
    if not ocls:
        MROClassable.process_mroclasses(ACls)
    AnticipatedMethod.process_antips(ACls)
    super(ACls).__init_subclass__()

class MROClassable(_ABC):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is MROClassable:
            if any('mroclasses' in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented

    @classmethod
    def update_mroclassnames(cls, ACls):
        try:
            mroclasses = list(ACls.mroclasses)
        except AttributeError:
            mroclasses = []
        for c in (c for c in ACls.__bases__ if issubclass(c, MROClassable)):
            try:
                basemroclasses = c.mroclasses
                mroclasses.extend(
                    name for name in basemroclasses if not name in mroclasses
                    )
            except AttributeError:
                pass
        ACls.mroclasses = tuple(mroclasses)

    @classmethod
    def get_inheritees(cls, ACls, name):
        inheritees = []
        for base in ACls.__bases__:
            if name in base.__dict__:
                if (altname := '_' + name + '_') in base.__dict__:
                    assert issubclass(getattr(base, name), Overclass)
                    inheritee = getattr(base, altname)
                else:
                    inheritee = getattr(base, name)
                inheritees.append(inheritee)
        inheritees = tuple(inheritees)
        new = ACls.__dict__[name] if name in ACls.__dict__ else None
        if inheritees:
            if new is None:
                return inheritees
            return (new, *inheritees)
        if new is not None:
            return (new,)
        return NotImplemented

    @classmethod
    def merge_mroclass(cls, ACls, name):
        inheritees = cls.get_inheritees(ACls, name)
        if inheritees is NotImplemented:
            return None, None
        if len(inheritees) == 1:
            mroclass = inheritees[0]
        else:
            mroclass = type(name, inheritees, {})
        if any(issubclass(c, Overclass) for c in inheritees):
            inheritees = (*inheritees, ACls)
            ocls = type(name, inheritees, {}, ocls = True)
        else:
            ocls = None
        return mroclass, ocls

    @classmethod
    def process_mroclass(cls, ACls, name):
        mroclass, ocls = cls.merge_mroclass(ACls, name)
        if mroclass is None:
            return
        if ocls is None:
            setattr(ACls, name, mroclass)
        else:
            setattr(ACls, '_' + name + '_', mroclass)
            setattr(ACls, name, ocls)

    @classmethod
    def update_mroclasses(cls, ACls):
        for name in ACls.mroclasses:
            cls.process_mroclass(ACls, name)

    @classmethod
    def process_mroclasses(cls, ACls):
        cls.update_mroclassnames(ACls)
        cls.update_mroclasses(ACls)

    def __new__(cls, ACls):
        '''Wrapper which adds mroclasses to ACls.'''
        if not any(issubclass(b, MROClassable) for b in ACls.__bases__):
            ACls.__init_subclass__ = classmethod(_mroclassable_init_subclass)
            cls.process_mroclasses(ACls)
        return ACls

###############################################################################

# from everest.mroclass import *
#
# @MROClassable
# class A:
#     def meth1(self):
#         return "Hello world!"
#     def meth2(self):
#         return 3
#
# class B(A):
#     mroclasses = 'InnerA',
#
# class C(A):
#     mroclasses = 'InnerB', 'Over',
#     @Overclass
#     class Over:
#         @AnticipatedMethod
#         def meth1(self):
#             '''Should return a string.'''
#         @AnticipatedMethod
#         def meth2(self):
#             '''Should return an integer'''
#         def meth3(self):
#             return self.meth1() * self.meth2()
#
# class D(B, C):
#     class InnerA:
#         def meth(self):
#             return 'foo'
#
# class E(D):
#     class InnerA:
#         def meth(self):
#             return ', '.join((super().meth(), 'bah'))
#     class InnerB:
#         ...
#
# class F(D):
#     def meth2(self):
#         return super().meth2() + 3
#     class Over:
#         def meth3(self):
#             return super().meth3().upper()
#
# myobj = E.InnerA()
# assert myobj.meth() == 'foo, bah'
#
# myobj = E.Over()
# assert myobj.meth3() == 'Hello world!Hello world!Hello world!'
#
# myobj = F.Over()
# assert myobj.meth3() == \
#     'HELLO WORLD!HELLO WORLD!HELLO WORLD!HELLO WORLD!HELLO WORLD!HELLO WORLD!'

###############################################################################
