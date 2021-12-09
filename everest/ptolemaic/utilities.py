###############################################################################
''''''
###############################################################################


from everest.classtools import add_defer_meths as _add_defer_meths


def add_defer_meths(*args, **kwargs):

    dec = _add_defer_meths(*args, **kwargs)

    def decorator(obj):
        with obj.clsmutable:
            return dec(obj)

    return decorator


###############################################################################
###############################################################################
