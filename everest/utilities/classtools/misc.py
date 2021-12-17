###############################################################################
''''''
###############################################################################


TEMPLATES = {
    dict: (
        '__getitem__', '__len__', '__iter__', '__contains__', 'keys',
        'items', 'values', 'get', '__eq__', '__ne__',
        )
    }


def add_defer_meth(
        obj, methname: str, defertoname: str, /, defermethname=None
        ):
    if mutable := hasattr(obj, 'clsfreezeattr'):
        prev = obj.clsfreezeattr
        obj.clsfreezeattr.toggle(False)
    try:
        if defermethname is None:
            defermethname = methname
        exec('\n'.join((
            f"@property",
            f"def {methname}(self, /):"
            f"    return self.{defertoname}.{defermethname}"
            )))
        setattr(obj, methname, eval(methname))
    finally:
        if mutable:
            obj.clsfreezeattr.toggle(prev)


def add_defer_meths(deferto, args=(), kwargs=None, /, like=None):

    if like is not None:
        args = (*args, *TEMPLATES[like])

    def decorator(obj):
        if args is not None:
            for methname in args:
                add_defer_meth(obj, methname, deferto)
        if kwargs is not None:
            for methname, defermethname in kwargs.items():
                add_defer_meth(obj, methname, deferto, defermethname)
        return obj

    return decorator


###############################################################################
###############################################################################
