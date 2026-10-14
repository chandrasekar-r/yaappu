"""Rule-licensed seer re-segmentation (fallback layer over venba.check_kural).

Only runs when the word-boundary checker rejects a line. Each license is a
named rule from Tamil prosody; candidates are tried in order of the number of
licensed edits (minimal change first), and the result records which licenses
were used.

L1  kutriyalikaram: a kutriyalukaram-final word before a ய-initial word turns
    its u into a half-length i that is not counted (யாப்பருங்கலக் காரிகை:
    குற்றியலிகரம் "அலகு பெறாது"): செல்வத்திற்கு யாதெனின் -> செல்வத்திற்க் யாதெனின்.
    Also the editorial form where that i was written onto the next word
    (எனப்படுவ தியாதெனின்): the token-initial C+ி before ய is moved back as a
    pure consonant onto the previous word (a licensed boundary shift).
L2  aikaarakkurukkam: non-initial ஐ in a word may scan as short (one edit per line).
"""
import itertools, re
from .venba import check_kural, Result
from .asai import ends_kutriyalukaram
from .graphemes import parse

VIRAMA, I_SIGN, AI_SIGN = "\u0BCD", "\u0BBF", "\u0BC8"
_PUNCT = re.compile(r"[^\u0B80-\u0BFF]")


def _l1_sites(words):
    sites = []
    for k in range(len(words) - 1):
        a, b = _PUNCT.sub("", words[k]), words[k + 1]
        if ends_kutriyalukaram(a) and b.startswith("ய"):
            sites.append(("L1", k, "u"))
        gb = parse(b)
        if len(gb) > 1 and gb[0].cons and gb[0].vowel == "i" and gb[0].text.endswith(I_SIGN) \
                and gb[1].text.startswith("ய") and parse(a) and not parse(a)[-1].is_mei:
            sites.append(("L1", k, "shift"))
    return sites


def _l2_sites(words):
    out = []
    for k, w in enumerate(words):
        gs = parse(_PUNCT.sub("", w))
        for j, g in enumerate(gs):
            if j > 0 and g.text.endswith(AI_SIGN):
                out.append(("L2", k, j))
    return out


def _apply(words, edits):
    ws = list(words)
    for kind, k, x in edits:
        if kind == "L1" and x == "u":
            a = _PUNCT.sub("", ws[k]); ws[k] = a[:-1] + VIRAMA
        elif kind == "L1":
            g0 = parse(ws[k + 1])[0].text
            ws[k] = _PUNCT.sub("", ws[k]) + g0[:-1] + VIRAMA; ws[k + 1] = ws[k + 1][len(g0):]
        elif kind == "L2":
            gs = [g.text for g in parse(_PUNCT.sub("", ws[k]))]
            gs[x] = gs[x][:-1]; ws[k] = "".join(gs)
    return ws


def check_kural_licensed(text: str, licenses=("L1",)) -> Result:
    """Default: L1 only. L2 is opt-in (it adds a shuffle false accept and recovers nothing on errata text)."""
    r = check_kural(text)
    if r.ok:
        return r
    words = text.replace("\n", " ").split()
    l1 = _l1_sites(words) if "L1" in licenses else []
    l2 = _l2_sites(words) if "L2" in licenses else []
    cands = [list(c) for n in range(1, len(l1) + 1) for c in itertools.combinations(l1, n)]
    cands.sort(key=len)
    l1sets = [[]] + cands
    for extra in [None] + l2:          # L2: at most one shortened ai, tried after pure L1
        for base in l1sets:
            edits = base + ([extra] if extra else [])
            if not edits:
                continue
            rr = check_kural(" ".join(_apply(words, edits)))
            if rr.ok:
                rr.detail = "licensed: " + ",".join(f"{a}@w{k+1}" for a, k, _ in edits)
                return rr
    return r
