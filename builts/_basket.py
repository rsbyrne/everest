from . import Built

class Basket(Built):
    def __init__(self, **kwargs):
        super().__init__()
    def __iter__(self):
        for key, inp in sorted(self.inputs.items()):
            yield (key, inp)
    def __len__(self):
        return len(self.inputs)
    def __getitem__(self, key):
        return self.inputs[key]
