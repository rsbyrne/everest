###############################################################################
''''''
###############################################################################


# from abc import ABCMeta as _ABCMeta
import weakref as _weakref


from .adderclass import AdderClass as _AdderClass


class MROClass(_AdderClass):

    _owner = None

    @_AdderClass.decorate(classmethod)
    def mroclass_init(cls, *, owner: type):
        cls._owner = _weakref.ref(owner)

    @_AdderClass.decorate(classmethod)
    def get_owner(cls):
        return cls._owner()


class Overclass(MROClass):

    overclasstag = None
    fixedoverclass = NotImplemented
    metaclassed = False

    @_AdderClass.decorate(classmethod)
    def overclass_init(cls, *, owner: type):
        cls.mroclass_init(owner=owner)


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


def add_classpath(outercls, innercls, name):
    if hasattr(outercls, 'classpath'):
        innercls.classpath = tuple((*outercls.classpath, name))
    innercls.classpath = (outercls, name)


@_AdderClass.wrapmethod
@classmethod
def extra_subclass_init(calledmeth, ACls, ocls=False):
    if not ocls:
        ACls._process_mroclasses(ACls)
    calledmeth()


def check_if_fuserclass(cls):
    return 'mroclassfuser' in cls.__dict__


def remove_duplicates(seq):
    out = []
    for thing in seq:
        if thing not in out:
            out.append(thing)
    return out


class MROClassable(_AdderClass):

    toadd = dict(
        __init_subclass__=extra_subclass_init,
        )

    mroclasses = ()

    @_AdderClass.hiddenmethod
    @classmethod
    def get_mroclassnames(cls, ACls):
        mroclasses = []
        if cls is not ACls:
            mroclasses.extend(cls.get_mroclassnames(cls))
        for name, att in ACls.__dict__.items():
            try:
                if issubclass(att, MROClass):
                    mroclasses.append(name)
            except TypeError:
                continue
        for c in ACls.__bases__:
            if issubclass(c, MROClassable):
                try:
                    mroclasses.extend(c.mroclasses)
                except AttributeError:
                    pass
        return tuple(remove_duplicates(mroclasses))

    @_AdderClass.hiddenmethod
    @classmethod
    def update_mroclassnames(cls, ACls):
        ACls.mroclasses = cls.get_mroclassnames(ACls)

    @_AdderClass.hiddenmethod
    @classmethod
    def get_inheritees(cls, ACls, name):
        inheritees = []
        if cls is not ACls:
            inheritees.extend(cls.get_inheritees(cls, name))
        for base in ACls.__bases__:
            if name in base.__dict__:
                if (altname := '_' + name + '_') in base.__dict__:
                    assert issubclass(getattr(base, name), Overclass)
                    inheritee = getattr(base, altname)
                else:
                    inheritee = getattr(base, name)
                if check_if_fuserclass(inheritee):
                    inheritees.extend(inheritee.__bases__)
                else:
                    inheritees.append(inheritee)
        new = ACls.__dict__[name] if name in ACls.__dict__ else None
        if new is not None:
            if check_if_fuserclass(new):
                inheritees = (*new.__bases__, *inheritees)
            else:
                inheritees = (new, *inheritees)
        return tuple(remove_duplicates(inheritees))

    @_AdderClass.hiddenmethod
    @classmethod
    def merge_mroclass(cls, ACls, name):
        inheritees = cls.get_inheritees(ACls, name)
        if not inheritees:
            return None, None
        if len(inheritees) == 1:
            mroclass = inheritees[0]
        else:
            mroclass = type(name, inheritees, dict(mroclassfuser=True))
            mroclass.mroclass_init(owner=ACls)
        if ocins := tuple((c for c in inheritees if issubclass(c, Overclass))):
            over = ACls
            for ocin in ocins:
                if (fixtag := ocin.fixedoverclass) is not NotImplemented:
                    if fixtag is None:
                        ocin.fixedoverclass = ACls
                    else:
                        over = fixtag
                    break
            if any(ocin.metaclassed for ocin in ocins):
                ocls = over(name, inheritees, {})
            else:
                ocls = type(name, (*inheritees, over), {}, ocls=True)
            ocls.overclass_init(owner=ACls)
        else:
            ocls = None
        return mroclass, ocls

    @_AdderClass.hiddenmethod
    @classmethod
    def process_mroclass(cls, ACls, name):
        mroclass, ocls = cls.merge_mroclass(ACls, name)
        if mroclass is None:
            return
        remove_abstractmethods(mroclass)
        if ocls is None:
            setattr(ACls, name, mroclass)
            add_classpath(ACls, mroclass, name)
        else:
            remove_abstractmethods(ocls)
            add_classpath(ACls, ocls, name)
            altname = '_' + name + '_'
            add_classpath(ACls, mroclass, altname)
            setattr(ACls, altname, mroclass)
            setattr(ACls, name, ocls)

    @_AdderClass.hiddenmethod
    @classmethod
    def update_mroclasses(cls, ACls):
        for name in ACls.mroclasses:
            cls.process_mroclass(ACls, name)

    @_AdderClass.hiddenmethod
    @classmethod
    def process_mroclasses(cls, ACls):
        cls.update_mroclassnames(ACls)
        cls.update_mroclasses(ACls)

    def __init_subclass__(cls, **kwargs):
        cls.process_mroclasses(cls)
        super().__init_subclass__(**kwargs)

    def __new__(cls, ACls):
        '''Wrapper which adds mroclasses to ACls.'''
        ACls = super().__new__(cls, ACls)
        ACls._process_mroclasses = cls.process_mroclasses
        if not any(issubclass(b, MROClassable) for b in ACls.__bases__):
            cls.process_mroclasses(ACls)
        return ACls


###############################################################################

###############################################################################
