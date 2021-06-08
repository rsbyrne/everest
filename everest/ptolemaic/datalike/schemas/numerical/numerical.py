###############################################################################
''''''
###############################################################################

from . import _classtools

from . import _Schema, _functional


@_classtools.Operable
class Numerical(_Schema):


    @classmethod
    def operate(cls, operator, *args, **kwargs):
        return _functional.Operation(operator, *args, **kwargs)


    @_classtools.IOperable
    class Var:

        __slots__ = (
            '_value', '_valuemode', '_modemeths',
            'get_value', 'set_value', 'del_value'
            )

        def __init__(self, *args, **kwargs):
            self._value = None
            self._valuemode = 0 # 0: null, 1: unrectified, 2: rectified
            self.get_value = self._get_value_mode0
            self.set_value = self._set_value_mode0
            self.del_value = self._del_value_mode0
            self._modemeths = { # pylint: disable=W0201
                0: ( # Null
                    self._get_value_mode0,
                    self._set_value_mode0,
                    self._del_value_mode0
                    ),
                1: ( # Setting
                    self._get_value_mode1,
                    self._set_value_mode1,
                    self._del_value_mode1
                    ),
                2: ( # Getting
                    self._get_value_mode2,
                    self._set_value_mode2,
                    self._del_value_mode2
                    ),
                }
            super().__init__(*args, **kwargs)

        def ioperate(self, operator, other, /):
            self.value = operator(self.value, other) # pylint: disable=W0201,E0237,E1101
            return self

        def rectify(self):
            self._value = self.dtype(self._value) # pylint: disable=E1101
        def nullify(self):
            self._value = None

        def _change_mode(self, valuemode: int):
            self.get_value, self.set_value, self.del_value = \
                self._modemeths[valuemode]
            self._valuemode = valuemode

        def _get_value_mode0(self): # pylint: disable=R0201
            raise ValueError('Null value detected.')
        def _set_value_mode0(self, val, /):
            self._change_mode(1)
            self.set_value(val)
        def _del_value_mode0(self):
            pass

        def _get_value_mode1(self):
            try:
                self.rectify()
                self._change_mode(2)
                return self._value
            except TypeError as exc1:
                self.del_value()
                try:
                    return self.get_value()
                except ValueError as exc2:
                    raise exc2 from exc1
        def _set_value_mode1(self, val, /):
            self._value = val
        def _del_value_mode1(self):
            self._change_mode(0)
            self.nullify()

        def _get_value_mode2(self):
            return self._value
        def _set_value_mode2(self, val, /):
            self._change_mode(1)
            self.set_value(val)
        def _del_value_mode2(self):
            self._change_mode(0)
            self.nullify()


###############################################################################
###############################################################################
