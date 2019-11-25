import random

class Reseed:
    def __init__(self, randomseed = None):
        if randomseed is None:
            randomseed = random.random()
        self.randomseed = randomseed
    def __enter__(self):
        random.seed(self.randomseed)
    def __exit__(self, *args):
        random.seed()

def wordhash(hashID, nWords = 2):
    with Reseed(hashID):
        wordhashlist = []
        for n in range(nWords):
            randindex = random.randint(0, (len(wordlist) - 1))
            wordhashlist.append(wordlist[randindex])
        wordhashstr = '-'.join(wordhashlist).replace('--', '-').lower()
    return wordhashstr

def _make_syllables():
    consonants = list("bcdfghjklmnpqrstvwxyz")
    conclusters = ['bl', 'br', 'dr', 'dw', 'fl', 'fr', 'gl', 'gr', 'kl', 'kr', 'kw', 'pl', 'pr', 'sf', 'sk', 'sl', 'sm', 'sn', 'sp', 'st', 'sw', 'tr', 'tw']
    condigraphs = ['sh', 'ch', 'th', 'ph']
    allcons = [*consonants, *conclusters, *condigraphs]
    vowels = [*list("aeiou")]
    syllables = [consonant + vowel for vowel in vowels for consonant in allcons]
    syllables.extend([vowel + syllable for vowel in vowels for syllable in syllables])
    syllables = list(sorted(syllables))
    return syllables

SYLLABLES = _make_syllables()

def random_syllable():
    syllable = random.choice(SYLLABLES)
    return syllable

def random_word(length = 3):
    outWord = ''
    for _ in range(length):
        outWord += random_syllable()
    return outWord

def random_phrase(phraselength = 2, wordlength = 3):
    phraseList = []
    for _ in range(phraselength):
        phraseList.append(
            random_word(wordlength)
            )
    phrase = "-".join(phraseList)
    return phrase

def get_random_word(randomseed = None, **kwargs):
    with Reseed(randomseed):
        output = random_word(**kwargs)
    return output

def get_random_phrase(randomseed = None, **kwargs):
    with Reseed(randomseed):
        output = random_phrase(**kwargs)
    return output
