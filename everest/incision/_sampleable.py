###############################################################################
''''''
###############################################################################


import functools as _functools
import collections.abc as _collabc


from ._sliceable import Sliceable as _Sliceable


def yield_criteria(*criteria):
    for criterion in criteria:
        if isinstance(criterion, tuple):
            yield from yield_criteria(*criterion)
        else:
            if not callable(criterion):
                raise TypeError("Criteria must be callable.")
            yield criterion


@_functools.lru_cache
def get_single_criterion_function(criterion):
    if isinstance(criterion, type):
        def checktype(arg, argtyp=criterion, /):
            return isinstance(arg, argtyp)
        return checktype
    if not callable(criterion):
        print(criterion, type(criterion))
        raise TypeError(criterion)
    return criterion


def get_criterion_function(*criteria):
    criteria = tuple(yield_criteria(criteria))
    critfuncs = tuple(map(get_single_criterion_function, criteria))
    if len(critfuncs) == 1:
        criterion_function = critfuncs[0]
    else:
        def criterion_function(arg, funcs=critfuncs, /):
            return all(func(arg) for func in funcs)
    criterion_function.criteria = criteria
    return criterion_function


def always_true(arg):
    return True


class Sampleable(_Sliceable):

    def __init__(self, /, *args, criterion=always_true, **kwargs):
        crfn = self.criterion_function = get_criterion_function(criterion)
        self.register_argskwargs(criterion=crfn.criteria)
        super().__init__(*args, **kwargs)

    def __contains__(self, item):
        if not super().__contains__(item):
            return False
        return self.criterion_function(item)

    @classmethod
    def slice_step_methods(cls, /):
        yield _collabc.Callable, cls.incise_sampler
        yield from super().slice_step_methods()

    def incise_sampler(self, sampler):
        return self.new_self(criterion=(self.criterion, sampler))


###############################################################################
###############################################################################
