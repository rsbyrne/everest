###############################################################################
''''''
###############################################################################


class Switch:

    __slots__ = ('_state',)

    def __init__(self, state: bool = False, /):
        self._state = state

    def toggle(self, state:bool=None, /):
        if state is None:
            state = not self._state
        self._state = bool(state)

    def __bool__(self, /):
        return self._state

    def __repr__(self, /):
        return f"<{self.__class__.__name__}({self._state})>"

    def as_(self, state: bool, /):
        return SwitchContext(self, state)


class SwitchContext:

    __slots__ = ('switch', 'state', '_prevstate')

    def __init__(self, switch: Switch, state: bool, /):
        self.switch, self.state = switch, state

    def __enter__(self, /):
        switch = self.switch
        self._prevstate = bool(switch)
        switch.toggle(self.state)

    def __exit__(self, /, *_):
        self.switch.toggle(self._prevstate)


###############################################################################
###############################################################################
