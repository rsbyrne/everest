class _PropertyController:
    def __init__(self, **subs):
        self._subs = subs
        self.__dict__.update(subs)
    def update(self):
        for sub in self._subs.values():
            self._update_sub(sub)
            sub.update()
    def _update_sub(self, sub):
        pass
    def __getitem__(self, key):
        return self._subs[key]

class _Vanishable(_PropertyController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._visible = True
        self._visibleMaster = True
    def _update_sub(self, sub):
        super()._update_sub(sub)
        sub._visibleMaster = self.visible
    @property
    def visible(self):
        return self._visible and self._visibleMaster
    @visible.setter
    def visible(self, value):
        self._visible = bool(value)
        self.update()
    def toggle(self):
        self.visible = not self.visible

class _Fadable(_PropertyController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._alpha = 1.
        self._alphaMaster = 1.
    def _update_sub(self, sub):
        super()._update_sub(sub)
        sub._alphaMaster = self.alpha
    @property
    def alpha(self):
        return self._alpha * self._alphaMaster
    @alpha.setter
    def alpha(self, value):
        self._alpha = float(value)
        self.update()
