################################################################################

from . import generic as _generic
import itertools as _itertools

def unpacker_zip(keys, vals):
    if isinstance(keys, _generic.FuncyUnpackable):
        if not isinstance(vals, _generic.FuncyUnpackable):
            vals = _itertools.repeat(vals)
        for subkeys, subvals in zip(keys, vals):
            yield from unpacker_zip(subkeys, subvals)
    else:
        yield keys, vals

def is_numeric(arg):
    try:
        _ = arg + 1
        return True
    except:
        return False

def kwargstr(**kwargs):
    outs = []
    for key, val in sorted(kwargs.items()):
        if not type(val) is str:
            try:
                val = val.namestr
            except AttributeError:
                try:
                    val = val.__name__
                except AttributeError:
                    val = str(val)
        outs.append(': '.join((key, val)))
    return '{' + ', '.join(outs) + '}'

def process_scalar(scal):
    return scal.dtype.type(scal)

################################################################################
