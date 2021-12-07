###############################################################################
''''''
###############################################################################


from everest import classtools as _classtools

from everest.ptolemaic import pleroma as _pleroma


class Ptolemaic(
        _classtools.ClassInit, _classtools.Freezable,
        metaclass=_pleroma.Pleromatic,
        ):
    ...


###############################################################################
###############################################################################
