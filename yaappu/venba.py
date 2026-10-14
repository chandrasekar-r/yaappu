"""Kural venba checker: seer types, venthalai (XOR) linkage, final-seer rule."""
from dataclasses import dataclass, field
from itertools import product
from typing import List, Optional
from .asai import asai_split, ends_kutriyalukaram, SEER_NAMES, NER, NIRAI, is_alabedai
from .graphemes import parse

FINAL_NAMES = {("ner",): "நாள்", ("nirai",): "மலர்", ("ner", "bu"): "காசு", ("nirai", "bu"): "பிறப்பு"}


@dataclass
class Result:
    ok: bool
    error: Optional[str] = None
    seers: List[str] = field(default_factory=list)
    detail: str = ""


import re
_INNER = re.compile("([கசடதபற])\u0BC1(?=[அஆஇஈஉஊஎஏஐஒஓஔ])")


def _elide(words):
    """Kutriyalukaram before a vowel-initial word loses its u (the consonant
    re-syllabifies onto the next word): நின்று + உலகம் -> நின்ற் | றுலகம்."""
    def inner(w):  # same rule inside a token written without sandhi (படிறுஇலவாம்)
        return _INNER.sub(lambda m: m.group(1) + ("\u0BC1" if not ends_kutriyalukaram(w[:m.end()]) else "\u0BCD"), w)
    out = [inner(w) for w in words]
    for k in range(len(out) - 1):
        nxt = parse(out[k + 1])
        if ends_kutriyalukaram(out[k]) and nxt and nxt[0].cons is None and nxt[0].vowel:
            out[k] = out[k][:-1] + "\u0BCD"
    return out


from .graphemes import SIGNS, VOWELS
_SIGN_OF = {v: k for k, v in SIGNS.items()}


def _resyllabify(w1, w2):
    """Puṇarchi across a word boundary: a final consonant takes the next word's initial
    vowel (துன்பம் + அஃது -> துன்பமஃ | து). The joined syllable (and the consonants that
    close it) is scanned with the first seer. Returns None if not applicable."""
    a, b = parse(w1), parse(w2)
    if not a or not b or not a[-1].is_mei or a[-1].cons == "\u0B83" or b[0].cons is not None:
        return None
    j = 1
    while j < len(b) and b[j].is_mei:
        j += 1
    if j >= len(b):
        return None
    joined = a[-1].cons + _SIGN_OF.get(b[0].vowel, "")
    return ("".join(g.text for g in a[:-1]) + joined + "".join(g.text for g in b[1:j]),
            "".join(g.text for g in b[j:]))


def _variants(words):
    """Word-boundary scansion plus every combination of boundary resyllabifications."""
    out = [list(words)]
    for k in range(len(words) - 1):
        new = []
        for v in out:
            r = _resyllabify(v[k], v[k + 1])
            if r:
                new.append(v[:k] + list(r) + v[k + 2:])
        out += new
    return out


def _readings(word: str):
    """Alabedai and aytham are optionally counted (isai-niraiththal); yield readings.
    Alabedai may or may not be counted as an asai (isai-niraiththal); yield both."""
    gs = parse(word)
    has_alb = any(k and is_alabedai(gs[k - 1], g) for k, g in enumerate(gs))
    alb = (True, False) if has_alb else (True,)
    ayt = (False, True) if "\u0B83" in word else (False,)
    for a in alb:
        for t in ayt:
            yield [x for x, _ in asai_split(word, a, t)]


def next_start_required(pattern) -> str:
    """Venthalai: 2-asai seer -> next starts with the opposite of its last asai (XOR);
    3-asai (kaai) seer -> next starts with ner."""
    if len(pattern) == 2:
        return NIRAI if pattern[-1] == NER else NER
    return NER


def final_pattern(word: str, pat):
    if len(pat) == 1:
        return tuple(pat)
    if len(pat) == 2 and pat[1] == NER and parse(word)[-1].vowel == "u" and parse(word)[-1].cons:
        return (pat[0], "bu")
    return None


def check_kural(text: str) -> Result:
    words = [w for w in text.replace("\n", " ").split() if parse(w)]
    if len(words) == 8:
        # seer boundaries need not match word boundaries: try joining one adjacent pair
        tries = [words[:k] + [_elide(words[k:k + 2])[0] + words[k + 1]] + words[k + 2:] for k in range(7)]
        results = [check_kural(" ".join(t)) for t in tries]
        good = [r for r in results if r.ok]
        if good:
            good[0].detail = "joined two words into one seer"; return good[0]
        return Result(False, "word_count", detail="8 words, no join scans")
    if len(words) != 7:
        return Result(False, "word_count", detail=str(len(words)))
    words = _elide(words)
    try:
        [list(_readings(w)) for w in words]
    except ValueError as e:
        return Result(False, "unscannable", detail=str(e))
    best = None
    for k, ws in enumerate(_variants(words)):
        try:
            options = [list(_readings(w)) for w in ws]
        except ValueError:
            continue
        for combo in product(*options):
            r = _check_combo(ws, combo)
            if r.ok:
                if k:
                    r.detail = "boundary resyllabification"
                return r
            best = best or r
    return best


def _check_combo(words, pats) -> Result:
    names = []
    for k, (w, p) in enumerate(zip(words[:6], pats[:6])):
        if len(p) not in (2, 3):
            return Result(False, "seer_length", names, f"seer{k+1} {w} {len(p)} asai")
        if len(p) == 3 and p[2] == NIRAI:
            return Result(False, "kani_seer", names, f"seer{k+1} {w} {SEER_NAMES[tuple(p)]}")
        names.append(SEER_NAMES[tuple(p)])
    fp = final_pattern(words[6], pats[6])
    if fp is None:
        return Result(False, "final_seer", names, f"{words[6]} {pats[6]}")
    names.append(FINAL_NAMES[fp])
    for k in range(6):
        need, got = next_start_required(pats[k]), pats[k + 1][0]
        if need != got:
            return Result(False, "thalai", names, f"{words[k]}->{words[k+1]} need {need}")
    return Result(True, seers=names)
