"""Prototype: seer re-segmentation search (does not modify yaappu/*).
When the word-boundary checker fails, search over shifted seer boundaries:
each of the 6 internal boundaries may move by up to MAXSHIFT graphemes
(a cut may never land before a pure consonant). Candidates are ranked by
total shift (minimal re-segmentation first). Also handles 8-word lines by
merging, and 6-word lines by splitting one word.
Usage: python3 scripts/reseg_search.py [MAXSHIFT]   (default 2)
"""
import json, sys, random, itertools, collections
sys.path.insert(0, ".")
from yaappu import check_kural
from yaappu.venba import _elide, _check_combo, _readings
from yaappu.graphemes import parse

MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 2

def segs(words):
    gs = [[g.text for g in parse(w)] for w in words]
    flat = [g for w in gs for g in w]
    mei = [g.is_mei for w in words for g in parse(w)]
    bounds, p = [], 0
    for w in gs[:-1]:
        p += len(w); bounds.append(p)
    opts = []
    for b in bounds:
        o = [b + d for d in range(-MAX, MAX + 1) if 0 < b + d < len(flat) and not mei[b + d]]
        opts.append(sorted(o, key=lambda x: abs(x - b)))
    cands = []
    for cuts in itertools.product(*opts):
        if any(cuts[i] >= cuts[i + 1] for i in range(len(cuts) - 1)):
            continue
        cost = sum(abs(c - b) for c, b in zip(cuts, bounds))
        if cost: cands.append((cost, cuts))
    cands.sort()
    for cost, cuts in cands:
        edges = (0,) + cuts + (len(flat),)
        yield cost, ["".join(flat[edges[i]:edges[i + 1]]) for i in range(len(edges) - 1)]

def check(ws):
    try:
        opts = [list(_readings(w)) for w in ws]
    except ValueError:
        return None
    for combo in itertools.product(*opts):
        if _check_combo(ws, combo).ok:
            return combo
    return None

def reseg(text):
    words = [w for w in text.replace("\n", " ").split() if parse(w)]
    pools = []
    if len(words) == 7: pools = [_elide(words)]
    elif len(words) == 8: pools = [_elide(words[:k] + [words[k] + words[k + 1]] + words[k + 2:]) for k in range(7)]
    elif len(words) == 6: pools = [_elide(words)]  # 6 -> split handled by shifting: append dummy split below
    for ws in pools:
        if len(ws) == 6:  # split the longest word in two at its midpoint, then shift
            i = max(range(6), key=lambda k: len(parse(ws[k])))
            g = [x.text for x in parse(ws[i])]; m = len(g) // 2
            ws = ws[:i] + ["".join(g[:m]), "".join(g[m:])] + ws[i + 1:]
        for cost, s in segs(ws):
            if check(s): return cost, s
    return None

d = json.load(open("data/thirukkural.json"))["kural"]
texts = {k["Number"]: k["Line1"] + " " + k["Line2"] for k in d}
base = {n for n, t in texts.items() if check_kural(t).ok}
rec = {}
for n, t in texts.items():
    if n in base: continue
    r = reseg(t)
    if r: rec[n] = r
tot = len(base) + len(rec)
print(f"MAXSHIFT={MAX} baseline {len(base)}/1330={100*len(base)/1330:.2f}%  +reseg {len(rec)} -> {tot}/1330={100*tot/1330:.2f}%")
for n, (c, s) in sorted(rec.items()): print(f"  {n} cost={c}: {' '.join(s)}")
# false-accept control: shuffled-word negatives that the baseline rejects
random.seed(0); neg = acc = 0
for t in list(texts.values())[:400]:
    w = t.split(); random.shuffle(w); s = " ".join(w)
    if check_kural(s).ok: continue
    neg += 1; acc += bool(reseg(s))
print(f"false-accept on {neg} baseline-rejected shuffled lines: {acc} ({100*acc/max(neg,1):.1f}%)")
