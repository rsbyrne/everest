###############################################################################
''''''
###############################################################################


from everest.ptolemaic.pleroma import Pleroma as _Pleroma
from everest.ptolemaic.tekton import Tekton as _Tekton


class Demiurge(metaclass=_Tekton):

    @classmethod
    def call(cls,
            meta: _Pleroma, name: str, bases: tuple = (), /,
            annotations: dict = None, namespace: dict = None
            ):
        if namespace is None:
            namespace = {}
        if annotations is not None:
            namespace['_extra_annotations__'] = annotations
        if not '_epitaph' in namespace:
            taph = cls.taphonomy
            epitaph = taph.custom_epitaph(*taph.posformat_callsig(
                cls, name, bases, annotations, namespace,
                ))
            namespace['_epitaph'] = epitaph
        outcls = meta(name, bases, namespace)
        return outcls


###############################################################################
###############################################################################
