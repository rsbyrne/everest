from itertools import product
def suite_list(**iterables):
    ks, vs = zip(*iterables.items())
    return [
        {k: v for k, v in zip(ks, item)}
            for item in product(*vs)
        ]

class VectorSet:
    def __init__(self, **inputSets):
        self.vectors = suite_list(**inputSets)
    def __iter__(self):
        return iter(self.vectors)

class SchemaIterator:
    def __init__(self,
            schema,
            space
            ):
        self.schema = schema
        self.space = space
    def __iter__(self):
        self.vectors = iter(VectorSet(**self.space))
        return self
    def __next__(self):
        return self.schema(**next(self.vectors))
