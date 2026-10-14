"""Export per-word metrical profiles of all corpus words -> data/yaappu_profiles.json.
Black-box fields come from scripts/probe_profiler.profile_v2 (probe kurals through
check_kural); requirement *sets* (which keep ambiguity) come from the checker's own
functions and are asserted to agree with the black-box bits.
Run: python3 scripts/export_profiles.py"""
import sys, json, re, collections
sys.path.insert(0, "."); sys.path.insert(0, "scripts")
from probe_profiler import profile_v2
from yaappu.venba import _readings, _elide, next_start_required
from yaappu.asai import NIRAI
from yaappu.graphemes import parse

d = json.load(open("data/thirukkural.json"))["kural"]
freq = collections.Counter(re.sub(r"[^\u0B80-\u0BFF]", "", w) for k in d for w in (k["Line1"] + " " + k["Line2"]).split())
freq.pop("", None)


def req_set(w, nxt):
    try:
        ps = [tuple(p) for p in _readings(_elide([w, nxt])[0])]
    except ValueError:
        return []
    return sorted({next_start_required(p) for p in ps if len(p) in (2, 3) and not (len(p) == 3 and p[2] == NIRAI)})


out = {}
for w, f in freq.items():
    p = profile_v2(w)
    try:
        opens = sorted({r[0] for r in _readings(w)})
    except ValueError:
        opens = []
    rc, rv = req_set(w, "கண்ணம்"), req_set(w, "அண்ணம்")
    bit = lambda s: None if not s else (1 if "ner" in s else 0)
    assert bit(rc) == p["next_c"] and bit(rv) == p["next_v"], w
    out[w] = {"freq": f, "starts_with_vowel": parse(w)[0].cons is None, "opening_bits": opens,
              "next_req_if_c": rc, "next_req_if_v": rv, "next_c": p["next_c"], "next_v": p["next_v"],
              "ambiguous_c": len(rc) == 2, "ambiguous_v": len(rv) == 2,
              "terminal": p["terminal_v2"], "terminal_open": p["open_terminal"] or []}
json.dump(out, open("data/yaappu_profiles.json", "w"), ensure_ascii=False, indent=0)
c = collections.Counter()
for v in out.values():
    c["words"] += 1; c["mid_usable"] += bool(v["next_req_if_c"] or v["next_req_if_v"]); c["terminal"] += v["terminal"]
print(dict(c))
