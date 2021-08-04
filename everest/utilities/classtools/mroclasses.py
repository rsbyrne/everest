###############################################################################
''''''
###############################################################################


# from abc import ABCMeta as _ABCMeta
import weakref as _weakref
import more_itertools as _moreitertools


from .adderclass import AdderClass as _AdderClass

def yield_classpath(cls):
    if 'mroclassowner' in cls.__dict__:
        yield from yield_classpath(cls.mroclassowner)
        yield cls.mroclassname
    else:
        yield cls

class MROClass(_AdderClass):

    ismroclass = True
    mroclassname = None
    mroclassowner = None

    @_AdderClass.decorate(classmethod)
    def get_classpath(cls):
        return tuple(yield_classpath(cls))


class Overclass(MROClass):

    isoverclass = True
    fixedoverclass = NotImplemented
    metaclassed = False


class Metaclassed(Overclass):
    metaclassed = True


def remove_abstractmethods(cls):

    abstracts = sorted(set((
        name for name, att in cls.__dict__.items()
        if hasattr(att, '__isabstractmethod__')
        )))

    if abstracts:
        parents = cls.__mro__[1:]
        for name in abstracts:
            if name[:2] == '__':
                continue
            for parent in parents:
                if hasattr(parent, name):
                    delattr(cls, name)
                    print(f"Deleted {name} from {cls}.")
                    break

@_AdderClass.wrapmethod
@classmethod
def extra_subclass_init(calledmeth, ACls):
    MROClassable.update_mroclasses(ACls)
    calledmeth()


def yield_mroclassnames(cls):
    seen = set()
    if issubclass(cls, Overclass):
        seen.update(yield_mroclassnames(cls.mroclassowner))
    for basecls in cls.__mro__:
        for name, att in tuple(basecls.__dict__.items()):
            if name == 'mroclassowner':
                continue
            if isinstance(att, type):
                try:
                    if issubclass(att, MROClass):
                        if name not in seen:
                            seen.add(name)
                            yield name
                except TypeError:
                    continue

class MROClassable(_AdderClass):

    toadd = dict(
        __init_subclass__=extra_subclass_init,
        )

    @_AdderClass.hiddenmethod
    @classmethod
    def get_inheritees(cls, ACls, name):
        inheritees = []
        for base in ACls.__bases__:
            if name in base.__dict__:
                inheritee = getattr(base, name)
                if inheritee is None:
                    print(ACls, base, name)
                    raise ValueError
                if 'overclassmrobases' in inheritee.__dict__:
                    inheritees.extend(inheritee.overclassmrobases)
                elif 'mroclassfuser' in inheritee.__dict__:
                    inheritees.extend(inheritee.__bases__)
                else:
                    inheritees.append(inheritee)
        if name in ACls.__dict__:
            new = ACls.__dict__[name]
            if 'mroclassfuser' in new.__dict__:
                inheritees = (*new.__bases__, *inheritees)
            else:
                inheritees = (new, *inheritees)
        return tuple(_moreitertools.unique_everseen(inheritees))

    @_AdderClass.hiddenmethod
    @classmethod
    def merge_mroclass(cls, ACls, name):
        inheritees = cls.get_inheritees(ACls, name)
        if not inheritees:
            return
        clskwargs = dict(mroclassowner=ACls, mroclassname=name)
        if ocins := tuple((c for c in inheritees if issubclass(c, Overclass))):
            over = ACls
            clskwargs.update(overclassmrobases=inheritees)
            for ocin in ocins:
                if (fixtag := ocin.fixedoverclass) is not NotImplemented:
                    if fixtag is None:
                        ocin.fixedoverclass = ACls
                    else:
                        over = fixtag
                    break
            if any(ocin.metaclassed for ocin in ocins):
                mroclass = over(name, inheritees, clskwargs)
            else:
                mroclass = type(name, (*inheritees, over), clskwargs)
        else:
            if len(inheritees) == 1:
                mroclass = inheritees[0]
            else:
                mroclass = type(name, inheritees, clskwargs)
        return mroclass

    @_AdderClass.hiddenmethod
    @classmethod
    def update_mroclasses(cls, ACls):
        for name in yield_mroclassnames(ACls):
            mroclass = cls.merge_mroclass(ACls, name)
            if mroclass is not None:
                setattr(ACls, name, mroclass)

    def __new__(cls, ACls):
        '''Wrapper which adds mroclasses to ACls.'''
        ACls = super().__new__(cls, ACls)
        if not any(issubclass(b, MROClassable) for b in ACls.__bases__):
            cls.update_mroclasses(ACls)
        return ACls


###############################################################################
###############################################################################
