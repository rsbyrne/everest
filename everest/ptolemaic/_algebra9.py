###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import deque as _deque
from collections.abc import Container as _Container
from weakref import WeakSet as _WeakSet
from fractions import Fraction as _Fraction
import itertools as _itertools

from .ousia import Ousia as _Ousia
from .system import System as _System
from .demiurge import Demiurge as _Demiurge
from .enumm import Enumm as _Enumm


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


class Phrase(metaclass=_System):

    head: POS
    body: ARGS['.']


class ParserError(Exception):

    ...


class Realm(metaclass=_System):

    @prop
    def _phrases(self, /):
        return _WeakSet()

    @_abc.abstractmethod
    def _contains_(self, phrase: Phrase, /, *, caller: 'Realm') -> bool:
        raise NotImplementedError

    def __contains__(self, other, /) -> bool:
        if not isinstance(other, Phrase):
            return False
        if other in (phrases := self._phrases):
            return True
        out = self._contains_(other, caller=self)
        if out:
            phrases.add(other)
        return out

    @_abc.abstractmethod
    def _enphrase_(self, tokens, /, *, caller):
        raise NotImplementedError

    def enphrase(self, tokens: SafeIterator, /, *, caller) -> Phrase:
        with tokens:
            phrase = self._enphrase_(tokens, caller=caller)
        self._phrases.add(phrase)
        return phrase

    def __call__(self, /, *tokens) -> Phrase:
        tokens = SafeIterator(tokens)
        phrase = self.enphrase(tokens, caller=self)
        if tokens:
            raise ParserError
        return phrase


class Fixity(metaclass=_Enumm):

    PREFIX: 'Denotes an operator where the sign precedes the operands.'
    INFIX: 'Denotes an operator where the sign is between the operands.'
    POSTFIX: 'Denotes an operator where the sign postcedes the operands.'
    JUX: 'Denotes an operator with no explicit sign.'


class Operator(metaclass=_Demiurge):


    marker: POS
    signature: ARGS

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.valencemap = cls.convert({
            kls.valence: kls for kls in cls._demiclasses_
            })

    @classmethod
    def _demiconvert_(cls, arg, /):
        if isinstance(arg, tuple):
            return cls(*arg)
        return NotImplemented

    @classmethod
    def _dispatch_(cls, params, /):
        signature = params.signature
        n = Ellipsis if Ellipsis in signature else len(signature)
        return cls.valencemap[n].partial(params.marker, *signature)


    class _DemiBase_(Realm):

        valence = NotImplemented

        marker: POS
        symbol: ... = CALLBACK('marker')
        fixity: Fixity = Fixity.JUX

        @classmethod
        def _parameterise_(cls, /, *args, **kwargs):
            params = super()._parameterise_(*args, **kwargs)
            if not isinstance(fixity := params.fixity, Fixity):
                params.fixity = Fixity[fixity]
            return params

        @prop
        def precedence(self, /):
            valence = self.valence
            if isinstance(valence, int):
                return _Fraction(1, valence+1)
            return 0.

        def _contains_(self, phrase, /, *, caller):
            if phrase.head is not self.marker:
                return False
            try:
                self.parse_tokens(SafeIterator(phrase.body), caller=caller)
            except ParserError:
                return False
            return True

        @prop
        def parse_tokens(self, /):
            fixity = self.fixity
            if fixity is Fixity.JUX:
                return self._parse_tokens_
            return getattr(self, f'_parse_tokens_{fixity.name.lower()}_')

        @_abc.abstractmethod
        def _parse_tokens_(self, tokens: SafeIterator, /, *, caller) -> tuple:
            raise NotImplementedError

        def _parse_tokens_prefix_(self, tokens, /, *, caller):
            if next(tokens) != self.symbol:
                raise ParserError
            return self._parse_tokens_(tokens, caller=caller)

        def _parse_tokens_postfix_(self, tokens, /, *, caller):
            parsed = self._parse_tokens_(tokens, caller=caller)
            if next(tokens) != self.symbol:
                raise ParserError
            return parsed

        def _filter_infixes(self, tokens, /):
            yield next(tokens)
            for tok in tokens:
                if tok != self.symbol:
                    raise StopIteration
                yield next(tokens)

        def _parse_tokens_infix_(self, tokens, /, *, caller):
            return self._parse_tokens_(
                SafeIterator(self._filter_infixes(tokens)),
                caller=caller,
                )

        def _enphrase_(self, tokens, /, *, caller):
            return Phrase(self.marker, *self.parse_tokens(tokens, caller=caller))


    class Nullary(demiclass):

        valence = 0

        def _parse_tokens_(self, tokens, /, *, caller):
            return ()


    class Unary(demiclass):

        valence = 1

        source: POS[_Container] = None

        def _parse_tokens_(self, tokens, /, *, caller):
            source = caller if (source := self.source) is None else source
            if (token := next(tokens)) in source:
                return (token,)
            raise ParserError


    class Binary(demiclass):

        valence = 2

        lsource: POS[_Container] = None
        rsource: POS[_Container] = CALLBACK('lsource')

        def _parse_tokens_(self, tokens, /, *, caller):
            lsource = caller if (lsource := self.lsource) is None else lsource
            rsource = caller if (rsource := self.rsource) is None else rsource
            if (ltok := next(tokens)) in lsource:
                if (rtok := next(tokens)) in rsource:
                    return (ltok, rtok)
            raise ParserError


    class Ennary(demiclass):

        valence = Ellipsis

        source: POS[_Container] = None

        def _parse_tokens_(self, tokens, /, *, caller):
            source = caller if (source := self.source) is None else source
            vals = tuple(tokens)
            if all(val in source for val in vals):
                return vals
            raise ParserError


class Grammar(Realm):

    operators: ARGS[Operator]

#     @classmethod
#     def sort_operators(cls, operators, /):
#         n = len(operators)
#         for valence in (0, 1, 2):
#             for op in operators:
#                 if op.valence == 
        

    @classmethod
    def _parameterise_(cls, /, *args, **kwargs):
        params = super()._parameterise_(*args, **kwargs)
        params.operators = tuple(_itertools.chain.from_iterable(
            grp for key, grp in _itertools.groupby(
                params.operators, key=lambda val: -val.precedence
            )))
        return params

    def _contains_(self, phrase, /, *, caller):
        return any(
            op._contains_(phrase, caller=caller)
            for op in self.operators
            )

    def _enphrase_(self, tokens, /, *, caller) -> Phrase:
        for op in self.operators:
            try:
                phrase = op.enphrase(tokens, caller=caller)
            except ParserError:
                continue
            break
        else:
            raise ParserError
        if tokens:
            return self.enphrase(
                SafeIterator(tokens, pre=(phrase,)),
                caller=caller,
                )
        return phrase


###############################################################################
###############################################################################
