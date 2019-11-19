from . import utilities
from . import value

_accepted_inputTypes = {
    type([]),
    type(0),
    type(0.),
    type('0')
    }

def _clean_inputs(inputs):

    cleanVals = {
        'args',
        'kwargs',
        'self',
        '__class__'
        }
    for val in cleanVals:
        if val in inputs:
            del inputs[val]

    for key, val in inputs.items():
        if type(val) == tuple:
            inputs[key] = list(val)
        if not type(val) in _accepted_inputTypes:
            raise Exception(
                "Type " + str(type(val)) + " not accepted."
                )

class Built:

    def __init__(
            self,
            inputs,
            filepath,
            iterate = None,
            out = None,
            initialise = None
            ):

        _clean_inputs(inputs)
        script = utilities.ToOpen(filepath)()
        hashID = utilities.wordhashstamp((script, inputs))

        if not iterate is None:
            count = value.Value(0)
            self.iterate = lambda: self._iterate_wrap(
                iterate,
                count
                )
            def go(n):
                for i in range(n):
                    self.iterate()
            self.go = go
            self.count = count
        if not out is None:
            self.out = lambda: self._out_wrap(
                out
                )
        if not initialise is None:
            self.initialise = lambda **inBuiltDict: self._initialise_wrap(
                initialise,
                count,
                inBuiltDict
                )
            self.initials = {}
            self.initials_hashIDs = {}

        self.script = script
        self.inputs = inputs
        self.hashID = hashID

    def _out_wrap(self, out):
        return out()

    def _iterate_wrap(self, iterate, count):
        count.value += 1
        return iterate()

    def _initialise_wrap(self, initialise, count, inBuiltDict):
        count.value = 0
        self.initials.update(inBuiltDict)
        inHashDict = {
            key: inBuilt.hashID \
                for key, inBuilt in sorted(self.initials.items())
                }
        self.initials_hashIDs.update(inHashDict)
        inDataDict = {
            key: inBuilt.out() \
                for key, inBuilt in sorted(self.initials.items())
                }
        initialise(**inDataDict)
