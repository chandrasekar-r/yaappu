"""Tamil grapheme parsing into prosodic units."""
from dataclasses import dataclass
from typing import List, Optional

VIRAMA = "\u0BCD"
AYTHAM = "\u0B83"
VOWELS = {"அ": "a", "ஆ": "aa", "இ": "i", "ஈ": "ii", "உ": "u", "ஊ": "uu",
          "எ": "e", "ஏ": "ee", "ஐ": "ai", "ஒ": "o", "ஓ": "oo", "ஔ": "au"}
SIGNS = {"\u0BBE": "aa", "\u0BBF": "i", "\u0BC0": "ii", "\u0BC1": "u", "\u0BC2": "uu",
         "\u0BC6": "e", "\u0BC7": "ee", "\u0BC8": "ai", "\u0BCA": "o", "\u0BCB": "oo", "\u0BCC": "au"}
CONSONANTS = set("கஙசஞடணதநபமயரலவழளறன")
GRANTHA = set("ஜஷஸஹ")
SHORT = {"a", "i", "u", "e", "o"}
VALLINAM = set("கசடதபற")


@dataclass
class Grapheme:
    text: str
    cons: Optional[str]   # consonant letter, or None for a bare vowel / aytham
    vowel: Optional[str]  # vowel name, or None for a pure consonant (mei)

    @property
    def is_mei(self) -> bool:
        return self.vowel is None

    @property
    def is_short(self) -> bool:
        return self.vowel in SHORT


def parse(word: str) -> List[Grapheme]:
    """Split a Tamil string into graphemes; non-Tamil characters are dropped."""
    out: List[Grapheme] = []
    i, n = 0, len(word)
    while i < n:
        ch = word[i]
        if ch in VOWELS:
            out.append(Grapheme(ch, None, VOWELS[ch])); i += 1
        elif ch == AYTHAM:
            out.append(Grapheme(ch, AYTHAM, None)); i += 1
        elif ch in CONSONANTS or ch in GRANTHA:
            nxt = word[i + 1] if i + 1 < n else ""
            if nxt == VIRAMA:
                out.append(Grapheme(ch + nxt, ch, None)); i += 2
            elif nxt in SIGNS:
                out.append(Grapheme(ch + nxt, ch, SIGNS[nxt])); i += 2
            else:
                out.append(Grapheme(ch, ch, "a")); i += 1
        else:
            i += 1
    return out
