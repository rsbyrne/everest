###############################################################################
''''''
###############################################################################


from collections import deque as _deque


class TakeError(Exception):

    ...


class SafeIterator:

    __slots__ = (
        'iterator', 'pre', 'post', 'contexts',
        )

    def __init__(self, iterator, /, pre=(), post=()):
        self.iterator = iter(iterator)
        self.pre, self.post = _deque(pre), _deque(post)
        self.contexts = _deque()
        self.add_context()

    def add_context(self, /):
        self.contexts.append(_deque())

    def complete_context(self, /):
        return tuple(self.contexts.pop())

    def fail_context(self, /):
        out = self.complete_context()
        self.extendleft(reversed(out))
        return out

    @property
    def taken(self, /):
        return self.contexts[-1]

    def __iter__(self, /):
        return self

    def __next__(self, /):
        if (pre := self.pre):
            out = pre.popleft()
        else:
            try:
                out = next(self.iterator)
            except StopIteration as exc:
                if (post := self.post):
                    out = post.popleft()
                else:
                    raise exc
        self.taken.append(out)
        return out

    @property
    def append(self, /):
        return self.post.append

    @property
    def appendleft(self, /):
        return self.pre.appendleft

    @property
    def pop(self, /):
        return self.post.pop

    @property
    def popleft(self, /):
        return self.pre.popleft

    @property
    def extend(self, /):
        return self.post.extend

    @property
    def extendleft(self, /):
        return self.pre.extendleft

    def take(self, num=0, /, limit=None):
        with self:
            out = _deque()
            while len(out) < num:
                try:
                    out.append(next(self))
                except StopIteration as exc:
                    raise TakeError from exc
            if limit is not None:
                if limit is Ellipsis:
                    out.extend(tuple(self))
                else:
                    while len(out) < limit:
                        try:
                            out.append(next(self))
                        except StopIteration:
                            pass
        return tuple(out)

    def __bool__(self, /):
        try:
            val = next(self)
        except StopIteration:
            return False
        self.appendleft(val)
        return True

    def __enter__(self, /):
        self.add_context()

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self.fail_context()


###############################################################################
###############################################################################
