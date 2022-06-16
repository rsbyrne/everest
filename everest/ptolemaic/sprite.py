###############################################################################
''''''
###############################################################################


from everest.armature import Armature as _Armature

from . import ptolemaic as _ptolemaic


@_ptolemaic.Ptolemaic.register
class Sprite(_Armature):

    def convert(cls, obj, /):
        return _ptolemaic.convert(obj)


@_ptolemaic.Ptolemaic.register
class _SpriteBase_(_Armature.BaseTyp):

    ...


Sprite.BaseTyp = _SpriteBase_


###############################################################################
###############################################################################
