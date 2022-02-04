###############################################################################
''''''
###############################################################################


def pretty(obj, p, cycle):
    try:
        meth = {
            dict: pretty_kwargs,
            tuple: pretty_tuple,
            }[type(obj)]
    except KeyError:
        p.pretty(obj)
    else:
        meth(obj, p, cycle)


def pretty_kwargs(obj, p, cycle, /, root=''):
    if cycle:
        p.text(root + '(...)')
        return
    if not obj:
        p.text(root + '()')
        return
    with p.group(4, root + '(', ')'):
        kwargit = iter(obj.items())
        p.breakable()
        key, val = next(kwargit)
        p.text(key)
        p.text(' = ')
        pretty(val, p, cycle)
        p.text(',')
        for key, val in kwargit:
            p.breakable()
            p.text(key)
            p.text(' = ')
            pretty(val, p, cycle)
            p.text(',')
        p.breakable()


def pretty_dict(obj, p, cycle, /, root=''):
    if cycle:
        p.text(root + '{...}')
        return
    if not obj:
        p.text(root + '{}')
        return
    with p.group(4, root + '{', '}'):
        kwargit = iter(obj.items())
        p.breakable()
        key, val = next(kwargit)
        p.text(key)
        p.text(': ')
        pretty(val, p, cycle)
        p.text(',')
        for key, val in kwargit:
            p.breakable()
            p.text(key)
            p.text(': ')
            pretty(val, p, cycle)
            p.text(',')
        p.breakable()


def pretty_tuple(obj, p, cycle, /, root=''):
    if cycle:
        p.text(root + '(...)')
        return
    if not obj:
        p.text(root + '()')
        return
    with p.group(4, root + '(', ')'):
        for val in obj:
            p.breakable()
            pretty(val, p, cycle)
            p.text(',')
        p.breakable()


###############################################################################
###############################################################################
