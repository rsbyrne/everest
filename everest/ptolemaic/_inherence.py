###############################################################################
''''''
###############################################################################


from everest.ptolemaic.ousia import Ousia as _Ousia, Sprite as _Sprite


class Inherence(_Ousia):

    ### Defining the mandatory basetype for instances of this metaclass:

    @classmethod
    def _get_basetyp(meta, /):
        try:
            return Sollus
        except NameError:
            return super()._get_basetyp()


class Sollus(metaclass=Eidos):

    _ptolemaic_knowntypes__ = (_Sprite,)


###############################################################################
###############################################################################
