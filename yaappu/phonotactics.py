"""Mozhimarapu: word-initial, word-final and consonant-cluster constraints."""
from typing import Tuple
from .graphemes import parse, AYTHAM

INITIAL_CONS = set("கசதநபமவயஞ")
FINAL_MEI = set("ஞணநமனயரலவழள")
_N = set("கசதபஙஞநமயவ")  # what may follow ய் ர் ழ்
# allowed (mei, next consonant) pairs inside a word
FOLLOW = {
    "க": "க", "ச": "ச", "த": "த", "ப": "ப",
    "ட": "டகசப", "ற": "றகசப",
    "ங": "ஙக", "ஞ": "ஞசய", "ந": "நதய", "ம": "மபயவ",
    "ண": "ணடகசஞபமயவ", "ன": "னறகசஞபமயவ",
    "ய": "ய" + "".join(_N), "ர": "".join(_N), "ழ": "".join(_N),
    "ல": "லகசபவய", "ள": "ளகசபவய", "வ": "வ",
}
NASAL_OF = {"க": "ங", "ச": "ஞ", "ட": "ண", "த": "ந", "ப": "ம", "ற": "ன"}


def check_word(word: str, junctions: bool = False) -> Tuple[bool, str]:
    """junctions=True also accepts an otherwise illegal cluster when it sits at a
    compound boundary written without sandhi (both halves are legal words), e.g. வான்நின்று."""
    gs = parse(word)
    ok, why, cut = _check(gs)
    if not ok and junctions and cut is not None:
        a, b = "".join(g.text for g in gs[:cut]), "".join(g.text for g in gs[cut:])
        if check_word(a)[0] and check_word(b, True)[0]:
            return True, "ok (unsandhied compound)"
    return ok, why


def _check(gs):
    """Returns (ok, reason, cut index of a failing cluster or None)."""
    if not gs:
        return False, "empty"
    f, l = gs[0], gs[-1]
    if f.is_mei or (f.cons and f.cons not in INITIAL_CONS):
        return False, f"bad initial {f.text}", None
    if l.is_mei and l.cons not in FINAL_MEI:
        return False, f"bad final {l.text}", None
    for i in range(len(gs) - 1):
        a, b = gs[i], gs[i + 1]
        if not a.is_mei or b.cons is None:
            continue
        if a.cons == AYTHAM:
            if b.cons not in "கசடதபற":
                return False, f"aytham before {b.text}", None
            continue
        if b.cons == AYTHAM:
            return False, f"cluster {a.text}{b.text}", None
        if b.cons not in FOLLOW.get(a.cons, ""):
            return False, f"cluster {a.text}{b.text}", i + 1
        if b.is_mei:  # three-consonant cluster: only ய்/ர்/ழ் + (geminate | nasal+stop)
            c = gs[i + 2] if i + 2 < len(gs) else None
            if a.cons not in "யரழ" or c is None or c.cons is None:
                return False, f"cluster {a.text}{b.text}", i + 1
            if not (c.cons == b.cons or NASAL_OF.get(c.cons) == b.cons):
                return False, f"cluster {a.text}{b.text}{c.text}", i + 1
    return True, "ok", None


GEMINATE_BEFORE = {"க": "க", "ச": "ச", "த": "த", "ப": "ப", "ங": "க",
                   "ட": "கசதப", "ற": "கசதப"}  # ட்/ற் arise from ள்/ல் sandhi


def _initial_ok(word: str) -> bool:
    g = parse(word)
    return bool(g) and not g[0].is_mei and (g[0].cons is None or g[0].cons in INITIAL_CONS)


def split_text(text: str):
    """Rebuild orthographic words: verse editions split words at seer boundaries
    (e.g. மற் | றாங்கே), so a token with an impossible initial is glued to the previous one."""
    toks = [t.strip(".,?!;:") for t in text.split()]
    words = []
    for t in toks:
        if not t:
            continue
        if words and not _initial_ok(t):
            words[-1] += t
        else:
            words.append(t)
    return words


def check_text(text: str, junctions: bool = False):
    """Check every word of a verse, allowing word-final stops created by boundary sandhi."""
    words = split_text(text)
    out = []
    for k, w in enumerate(words):
        ok, why = check_word(w, junctions)
        if not ok and why.startswith("bad final") and k + 1 < len(words):
            last, nxt = parse(w)[-1], parse(words[k + 1])[0]
            if nxt.cons and nxt.cons in GEMINATE_BEFORE.get(last.cons, ""):
                ok2, why2 = check_word(w[:-2], junctions)
                ok, why = (True, "ok (boundary sandhi)") if ok2 or why2.startswith("bad final") else (False, why2)
        out.append((w, ok, why))
    return out
