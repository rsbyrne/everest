import random
import os

parentPath = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(parentPath, '_namesources', 'cities.txt'), mode = 'r') as file:
    CITIES = file.read().split('\n')
with open(os.path.join(parentPath, '_namesources', 'english_words.txt'), mode = 'r') as file:
    WORDS = file.read().split('\n')

class Reseed:
    def __init__(self, randomseed = None):
        if randomseed is None:
            randomseed = random.random()
        self.randomseed = randomseed
    def __enter__(self):
        random.seed(self.randomseed)
    def __exit__(self, *args):
        random.seed()

from functools import wraps
def reseed(func):
    @wraps(func)
    def wrapper(*args, randomseed = None, **kwargs):
        with Reseed(randomseed):
            return func(*args, **kwargs)
    return wrapper

def _make_syllables():
    consonants = list("bcdfghjklmnpqrstvwxyz")
    conclusters = [
        'bl', 'br', 'dr', 'dw', 'fl',
        'fr', 'gl', 'gr', 'kl', 'kr',
        'kw', 'pl', 'pr', 'sf', 'sk',
        'sl', 'sm', 'sn', 'sp', 'st',
        'sw', 'tr', 'tw'
        ]
    condigraphs = [
        'sh', 'ch', 'th', 'ph', 'zh',
        'ts', 'tz', 'ps', 'ng', 'sc',
        'gh', 'rh', 'wr'
        ]
    allcons = [*consonants, *conclusters, *condigraphs]
    vowels = [*list("aeiou")]
    voweldiphthongs = [
        'aa', 'ae', 'ai', 'ao', 'au',
        'ea', 'ee', 'ei', 'eo', 'eu',
        'ia', 'ie', 'ii', 'io', 'iu',
        'oa', 'oe', 'oi', 'oo', 'ou',
        'ua', 'ue', 'ui', 'uo', 'uu'
        ]
    allvowels = [*vowels, *voweldiphthongs]
    cvs = [consonant + vowel for vowel in allvowels for consonant in allcons]
    vcs = [vowel + consonant for consonant in allcons for vowel in allvowels]
    vcvs = [vowel + cv for vowel in allvowels for cv in cvs]
    cvcs = [consonant + vc for consonant in allcons for vc in vcs]
    syllables = [*cvs, *vcs, *vcvs, *cvcs]
    syllables = list(sorted(set(syllables)))
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

def random_phrase(phraselength = 2, wordlength = 2):
    # 2 * 2 yields 64 bits of entropy
    phraseList = []
    for _ in range(phraselength):
        phraseList.append(
            random_word(wordlength)
            )
    phrase = "-".join(phraseList)
    return phrase

def random_alphanumeric(length = 6):
    characters = 'abcdefghijklmnopqrstuvwxyz0123456789'
    choices = [random.choice(characters) for i in range(length)]
    return ''.join(choices)

@reseed
def get_random_alphanumeric(**kwargs):
    return random_alphanumeric(**kwargs)

@reseed
def get_random_word(**kwargs):
    output = random_word(**kwargs)

@reseed
def get_random_phrase(**kwargs):
    return random_phrase(**kwargs)

@reseed
def get_random_mix(**kwargs):
    phrase = random_phrase(phraselength = 1)
    alphanum = random_alphanumeric()
    output = '-'.join((phrase, alphanum))
    return output

@reseed
def get_random_cityword():
    return '-'.join([random.choice(s) for s in [CITIES, WORDS]])
