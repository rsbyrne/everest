###############################################################################
''''''
###############################################################################


def add_defer_meth(
        obj, methname: str, defertoname: str, /, defermethname=None
        ):
    if defermethname is None:
        defermethname = methname
    exec('\n'.join((
        f"@property",
        f"def {methname}(self, /):"
        f"    return self.{defertoname}.{defermethname}"
        )))
    setattr(obj, methname, eval(methname))


def add_defer_meths(deferto, *args, **kwargs):

    def decorator(obj):
        for methname in args:
            add_defer_meth(obj, methname, deferto)
        for methname, defermethname in kwargs.items():
            add_defer_meth(obj, methname, deferto, defermethname)
        return obj

    return decorator


###############################################################################
###############################################################################
