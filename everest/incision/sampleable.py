###############################################################################
''''''
###############################################################################


from .sliceable import Sliceable as _Sliceable


class _Sampling_:

    def __init__(self, *args, sampler, **kwargs):
        sampler = self.sampler = self.process_sampler(sampler)
        self.register_argskwargs(sampler=sampler)
        super().__init__(*args, **kwargs)

    @classmethod
    def process_sampler(cls, sampler):
        return sampler

    @classmethod
    def combine_samplers(self, a, b):
        '''Combines multiple samplers into one.'''
        return (a, b)

    def incise_sampler(self, sampler, /, *, context):
        '''Captures the sense of `context[::sampler]`'''
        sampler = self.combine_samplers(self.sampler, sampler)
        return super().incise_sampler(sampler, context=context)


class Sampleable(_Sliceable):

    @classmethod
    def child_classes(cls):
        yield from super().child_classes()
        yield _Sampling_

    @classmethod
    def slice_methods(cls, /):
        yield (False, False, True), cls.incise_sampler_slice
        yield from super().slice_methods()

    def incise_sampler(self, sampler, /, *, context):
        '''Captures the sense of `context[::sampler]`'''
        return self.Sampling(
            *self.args,
            **(self.kwargs | dict(sampler=sampler)),
            )

    def incise_sampler_slice(self, _, __, sampler, /, *, context):
        return self.incise_sampler(sampler, context=context)


###############################################################################
###############################################################################
