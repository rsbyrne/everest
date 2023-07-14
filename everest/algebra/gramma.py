###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import abc as _collabc
from weakref import WeakSet as _WeakSet
from fractions import Fraction as _Fraction
import itertools as _itertools

from everest.ptolemaic.ousia import Ousia as _Ousia
from everest.ptolemaic.system import System as _System
from everest.ptolemaic.demiurge import Demiurge as _Demiurge
from everest.ptolemaic.enumm import Enumm as _Enumm

from .utilities.safeiterator import SafeIterator as _SafeIterator


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

    def enphrase(self, tokens: _SafeIterator, /, *, caller) -> Phrase:
        with tokens:
            phrase = self._enphrase_(tokens, caller=caller)
        self._phrases.add(phrase)
        return phrase

    def __getitem__(self, tokens: _collabc.Iterator, /) -> Phrase:
        tokens = _SafeIterator(tokens)
        phrase = self.enphrase(tokens, caller=self)
        if tokens:
            return phrase, tokens
            # raise ParserError
        return phrase


class Fixity(metaclass=_Enumm):

    PREFIX: 'Denotes an operator where the sign precedes the operands.'
    INFIX: 'Denotes an operator where the sign is between the operands.'
    POSTFIX: 'Denotes an operator where the sign postcedes the operands.'
    JUX: 'Denotes an operator with no explicit sign.'


class Opp(metaclass=_Demiurge):


    marker: POS
    signature: ARGS
    oppkwargs: KWARGS

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
        signature = list(params.signature)
        try:
            signature.remove(Ellipsis)
        except IndexError:
            n = len(signature)
        else:
            n = Ellipsis
        return cls.valencemap[n].partial(
            params.marker, *signature, **params.oppkwargs
            )


    class _DemiBase_(Realm):

        valence = NotImplemented

        marker: POS
        symbol: KW = CALLBACK('marker')

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
                self.parse_tokens(_SafeIterator(phrase.body), caller=caller)
            except ParserError:
                return False
            return True

        @_abc.abstractmethod
        def _parse_tokens_(self, tokens: _SafeIterator, /, *, caller) -> tuple:
            raise NotImplementedError

        def _parse_tokens_prefix_(self, tokens, /, *, caller):
            if next(tokens) != self.symbol:
                raise ParserError
            return self._parse_tokens_(tokens, caller=caller)

        @prop
        def parse_tokens(self, /):
            return self._parse_tokens_prefix_

        def _enphrase_(self, tokens, /, *, caller):
            return Phrase(self.marker, *self.parse_tokens(tokens, caller=caller))


    class Nullary(demiclass):

        valence = 0

        def _parse_tokens_(self, tokens, /, *, caller):
            return ()


    class NonNullary(mroclass, metaclass=_System):

        fixity: KW[Fixity] = Fixity.JUX

        @classmethod
        def _parameterise_(cls, /, *args, **kwargs):
            params = super()._parameterise_(*args, **kwargs)
            if not isinstance(fixity := params.fixity, Fixity):
                params.fixity = Fixity[fixity]
            return params

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
                _SafeIterator(self._filter_infixes(tokens)),
                caller=caller,
                )

        @prop
        def parse_tokens(self, /):
            fixity = self.fixity
            if fixity is Fixity.JUX:
                return self._parse_tokens_
            return getattr(self, f'_parse_tokens_{fixity.name.lower()}_')


    class Unary(demiclass('.NonNullary')):

        valence = 1

        source: POS[_collabc.Container] = None

        def _parse_tokens_(self, tokens, /, *, caller):
            source = caller if (source := self.source) is None else source
            if (token := next(tokens)) in source:
                return (token,)
            raise ParserError


    class Binary(demiclass('.NonNullary')):

        valence = 2

        lsource: POS[_collabc.Container] = None
        rsource: POS[_collabc.Container] = CALLBACK('lsource')

        def _parse_tokens_(self, tokens, /, *, caller):
            lsource = caller if (lsource := self.lsource) is None else lsource
            rsource = caller if (rsource := self.rsource) is None else rsource
            if (ltok := next(tokens)) in lsource:
                if (rtok := next(tokens)) in rsource:
                    return (ltok, rtok)
            raise ParserError


    class Ennary(demiclass('.NonNullary')):

        valence = Ellipsis

        source: POS[_collabc.Container] = None

        def _parse_tokens_(self, tokens, /, *, caller):
            source = caller if (source := self.source) is None else source
            vals = tuple(tokens)
            if all(val in source for val in vals):
                return vals
            raise ParserError


class Gramma(Realm):

    opps: ARGS[Opp]        

    @classmethod
    def _parameterise_(cls, /, *args, **kwargs):
        params = super()._parameterise_(*args, **kwargs)
        opps = (
            Opp(*opp) if not isinstance(opp, Opp) else opp
            for opp in params.opps
            )
        params.opps = tuple(_itertools.chain.from_iterable(
            grp for key, grp in _itertools.groupby(
                opps, key=lambda val: -val.precedence
            )))
        return params

    def _contains_(self, phrase, /, *, caller):
        return any(
            op._contains_(phrase, caller=caller)
            for op in self.opps
            )

    def _enphrase_(self, tokens, /, *, caller) -> Phrase:
        for op in self.opps:
            try:
                phrase = op.enphrase(tokens, caller=caller)
            except ParserError:
                continue
            break
        else:
            raise ParserError
        if tokens:
            return self.enphrase(
                _SafeIterator(tokens, pre=(phrase,)),
                caller=caller,
                )
        return phrase


###############################################################################
###############################################################################
