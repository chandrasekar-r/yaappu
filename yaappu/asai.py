"""Asai (metrical syllable) segmentation and seer (metrical foot) naming.

Ner  = one syllable (short or long) + optional closing consonants.
Nirai = short syllable + following syllable (short or long) + optional consonants.
"""
from typing import List, Tuple
from .graphemes import parse, Grapheme, VALLINAM

NER, NIRAI = "ner", "nirai"
# long vowel -> short vowel letter that may follow it as alabedai
ALABEDAI = {"aa": "அ", "ii": "இ", "uu": "உ", "ee": "எ", "ai": "இ", "oo": "ஒ", "au": "உ"}


def is_alabedai(prev: Grapheme, g: Grapheme) -> bool:
    """A bare vowel letter written after a syllable carrying the matching long vowel."""
    return g.cons is None and g.vowel is not None and ALABEDAI.get(prev.vowel) == g.text


def asai_split(word: str, alabedai_counts: bool = True, aytham_counts: bool = False) -> List[Tuple[str, str]]:
    """Return [(asai, text)]. Raises ValueError if the word cannot be scanned."""
    gs = parse(word)
    if not gs:
        raise ValueError("empty")
    if alabedai_counts is False:
        gs = [g for k, g in enumerate(gs) if not (k and is_alabedai(gs[k - 1], g))]
    if aytham_counts:  # aytham scanned as a short (kuril-valued) unit
        gs = [Grapheme(g.text, None, "a") if g.cons == "\u0B83" else g for g in gs]
    out, i, n = [], 0, len(gs)
    while i < n:
        g = gs[i]
        if g.is_mei:
            if not out:
                raise ValueError("leading consonant")
            kind, txt = out[-1]; out[-1] = (kind, txt + g.text); i += 1; continue
        if g.is_short and i + 1 < n and not gs[i + 1].is_mei:
            j, kind = i + 2, NIRAI
        else:
            j, kind = i + 1, NER
        while j < n and gs[j].is_mei:
            j += 1
        out.append((kind, "".join(x.text for x in gs[i:j]))); i = j
    return out


def ends_kutriyalukaram(word: str) -> bool:
    """Word-final short u on a hard consonant, not in a lone-short-syllable word (e.g. அது)."""
    gs = parse(word)
    if len(gs) < 2 or gs[-1].vowel != "u" or gs[-1].cons not in VALLINAM:
        return False
    return not (len(gs) == 2 and gs[0].is_short)


SEER_NAMES = {
    (NER, NER): "தேமா", (NIRAI, NER): "புளிமா", (NIRAI, NIRAI): "கருவிளம்", (NER, NIRAI): "கூவிளம்",
    (NER, NER, NER): "தேமாங்காய்", (NIRAI, NER, NER): "புளிமாங்காய்",
    (NIRAI, NIRAI, NER): "கருவிளங்காய்", (NER, NIRAI, NER): "கூவிளங்காய்",
    (NER, NER, NIRAI): "தேமாங்கனி", (NIRAI, NER, NIRAI): "புளிமாங்கனி",
    (NIRAI, NIRAI, NIRAI): "கருவிளங்கனி", (NER, NIRAI, NIRAI): "கூவிளங்கனி",
}
