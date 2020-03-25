import operator
import numpy as np

from .utilities import flatten_dict

class Fetch:

    _fnDict = {}
    _fnDict.update(operator.__dict__)

    def __init__(
            self,
            *args,
            operation = None,
            opTag = None
            ):
        if type(operation) is str:
            opTag = operation
            operation = self._fnDict[operation]
        elif opTag is None:
            opTag = 'Fetch'

        self.args = args
        self.operation = operation
        self.opTag = opTag
        self.ID = str(self)

    def __repr__(self):
        ID = self.opTag + '({0})'.format(
            ', '.join([
                str(arg) \
                    for arg in self.args
                ])
            )
        return ID

    def __reduce__(self):
        return (Fetch, (self.args, self.operation, self.opTag))

    @classmethod
    def _operate(cls, *args, operation = None, context = None, scope = None):
        operands = []
        for arg in args:
            if type(arg) is Fetch:
                opVals = arg(context, scope)
            else:
                opVals = np.array(arg)
            operands.append(opVals)
        dictOperands = [
            operand for operand in operands if type(operand) is dict
            ]
        allkeys = list()
        for dictOperand in dictOperands:
            allkeys.extend(list(dictOperand.keys()))
        allkeys = set(allkeys)
        filteredOperands = []
        for operand in operands:
            if type(operand) is dict:
                missingKeys = [
                    key \
                        for key in allkeys \
                            if not key in operand
                    ]
                for key in missingKeys:
                    operand[key] = np.nan
            else:
                operand = {key: operand for key in allkeys}
            filteredOperands.append(operand)
        operands = filteredOperands
        outDict = dict()
        for key in allkeys:
            keyops = [operand[key] for operand in operands]
            try:
                evalVal = operation(*keyops)
            except TypeError:
                evalVal = None
            outDict[key] = evalVal
        return outDict

    @staticmethod
    def _process(inDict, context, scope = None):
        outs = set()
        if scope is None:
            checkkey = lambda key: True
        elif type(scope) is Scope:
            checkkey = lambda key: key in scope.keys()
        else:
            raise TypeError
        for key, result in sorted(inDict.items()):
            superkey = key.split('/')[0]
            if checkkey(superkey):
                indices = None
                try:
                    if result:
                        indices = '...'
                except ValueError:
                    if np.all(result):
                        indices = '...'
                    elif np.any(result):
                        countsPath = '/'.join((
                            superkey,
                            'outputs',
                            'count'
                            ))
                        counts = context(countsPath)
                        indices = counts[result.flatten()]
                        indices = tuple(indices)
                except:
                    raise TypeError
                if not indices is None:
                    outs.add((superkey, indices))
            else:
                pass
        return outs

    def __call__(self, context, scope = None):
        if self.operation is None:
            out = context(self.args)
        else:
            out = self._operate(
                *self.args,
                operation = self.operation,
                context = context
                )
        processed = self._process(out, context, scope)
        return out

    # def rekey(self):
    #     return Fetch(self, operation = 'rekey')

    def fn(self, operation, args):
        return Fetch(
            *(self, *args),
            operation = operation,
            opTag = None
            )

    def __lt__(*args): # <
        return Fetch(*args, operation = '__lt__')
    def __le__(*args): # <=
        return Fetch(*args, operation = '__le__')
    def __eq__(*args): # ==
        return Fetch(*args, operation = '__eq__')
    def __ne__(*args): # !=
        return Fetch(*args, operation = '__ne__')
    def __ge__(*args): # >=
        return Fetch(*args, operation = '__ge__')
    def __gt__(*args): # >
        return Fetch(*args, operation = '__gt__')
    def __neg__(*args): # -
        return Fetch(*args, operation = '__neg__')
    def __abs__(*args): # abs
        return Fetch(*args, operation = '__abs__')
    def __add__(*args): # +
        return Fetch(*args, operation = '__add__')
    def __sub__(*args): # -
        return Fetch(*args, operation = '__sub__')
    def __mul__(*args): # *
        return Fetch(*args, operation = '__mul__')
    def __div__(*args): # /
        return Fetch(*args, operation = '__div__')
    def __pow__(*args): # **
        return Fetch(*args, operation = '__pow__')
    def __floordiv__(*args): # //
        return Fetch(*args, operation = '__floordiv__')
    def __mod__(*args): # %
        return Fetch(*args, operation = '__mod__')
    def __contains__(*args): # in
        return Fetch(*args, operation = '__contains__')
    def __invert__(*args): # ~
        return Fetch(*args, operation = '__invert__')

    def __or__(*args): # |
        return Fetch(
            *args,
            operation = np.logical_or,
            opTag = '__union__'
            )
    @staticmethod
    def _diff_op(arg1, arg2):
        return np.logical_and(arg1, ~arg2)
    def __lshift__(*args): # <<
        return Fetch(
            *args,
            operation = args[0]._diff_op,
            opTag = '__difference__'
            )
    def __rshift__(*args): # <<
        return Fetch(
            *args[::-1],
            operation = args[0]._diff_op,
            opTag = '__difference__'
            )
    def __and__(*args): # &
        return Fetch(
            *args,
            operation = np.logical_and,
            opTag = '__intersection__'
            )
    def __xor__(*args): # ^
        return Fetch(
            *args,
            operation = np.logical_xor,
            opTag = '__symmetric__'
            )
