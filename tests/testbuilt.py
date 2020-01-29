from decimal import Decimal, getcontext
getcontext().prec=100

from ..value import Value
from ..builts.producer import Iterator

print sum(1/Decimal(16)**k *
          (Decimal(4)/(8*k+1) -
           Decimal(2)/(8*k+4) -
           Decimal(1)/(8*k+5) -
           Decimal(1)/(8*k+6)) for k in range(100))

class TestBuilt(Iterator):
    @staticmethod
    def kth(k):
        val = 1 / Decimal(16)**k * (
            Decimal(4)/(8*k+1) \
            - Decimal(2)/(8*k+4) \
            - Decimal(1)/(8*k+5) \
            - Decimal(1)/(8*k+6)
            )
        return val
    def __init__(self, **inputs):
        state = Value(0)
        self.outkeys = ['pi']
        super().__init__(self, initialiseFn, iterateFn, outFn, outkeys, loadFn)
    def out(self):
        return [self.state.value,]
    def initialise(self):
        self.state.value = 0
    def iterate(self):
        self.state.value += self.kth(self.count)

    def load(self, loadDict):
        for key, loadData in sorted(loadDict.items()):
            if key == 'modeltime':
                self.modeltime.value = loadData
            else:
                var = self.varsOfState[key]
                assert hasattr(var, 'mesh'), \
                    'Only meshVar supported at present.'
                nodes = var.mesh.data_nodegId
                for index, gId in enumerate(nodes):
                    var.data[index] = loadData[gId]

    def out(self):
        outs = []
        for key in self.outkeys:
            if key == 'modeltime':
                outs.append(self.modeltime())
            else:
                var = self.varsOfState[key]
                data = fieldops.get_global_var_data(var)
                outs.append(data)
        return outs
