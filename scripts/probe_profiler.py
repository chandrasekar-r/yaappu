"""Black-box word profiler for yaappu: probe kurals through the real check_kural.
Does not touch decoder/EVAL files. Run: python3 scripts/probe_profiler.py
"""
import sys, json, time, re, collections
sys.path.insert(0, ".")
from yaappu import check_kural
from yaappu.venba import _readings, _elide, next_start_required, final_pattern
from yaappu.asai import NER, NIRAI

TAIL = "மலரும் மலரும் மலரும் மலரும் உலகு"
PROBES = {("C", NER): "கண்ணம்", ("C", NIRAI): "மலரும்", ("V", NER): "அண்ணம்", ("V", NIRAI): "அலரும்"}
NER_PRED = "மலர்ந்தானே"  # nirai ner ner (புளிமாங்காய்), vowel-final so no puṇarchi with w -> successor must open ner
NIRAI_PRED = "பிறவி"  # nirai ner, vowel-final -> successor must open nirai


def ok(t):
    return check_kural(t).ok


def _bit(w, kind):
    a = ok(f"{w} {PROBES[(kind, NER)]} {TAIL}")
    b = ok(f"{w} {PROBES[(kind, NIRAI)]} {TAIL}")
    return (1 if a else 0 if b else None), (a and b)


def profile_word_with_yaappu(w):
    """Design as proposed. next_c/next_v: 1 = w needs a ner-initial successor
    (consonant-/vowel-initial), 0 = nirai, None = neither probe passes."""
    nc, amb_c = _bit(w, "C")
    nv, amb_v = _bit(w, "V")
    t1 = ok(f"கண்ணம் {'மலரும் ' * 5}{w}")
    t2 = ok(f"கண்ணம் {'மலரும் ' * 4}பிறவி {w}")
    rest = TAIL.split(" ", 1)[1]
    return {"word": w, "next_c": nc, "next_v": nv, "ambiguous_c": amb_c, "ambiguous_v": amb_v,
            "terminal": t1 or t2,
            "open_after_kannam": ok(f"கண்ணம் {w} {rest}"),
            "open_after_piravi": ok(f"பிறவி {w} {rest}")}


def profile_v2(w):
    """Fixed: terminal/opening also tested after a ner-requiring kaai predecessor."""
    p = profile_word_with_yaappu(w)
    o_nirai = ok(f"கண்ணம் {'மலரும் ' * 4}{NIRAI_PRED} {w}")
    o_ner = ok(f"கண்ணம் {'மலரும் ' * 4}{NER_PRED} {w}")
    p["terminal_v2"] = o_nirai or o_ner
    p["open_terminal"] = sorted(x for x, f in (("ner", o_ner), ("nirai", o_nirai)) if f) or None
    return p


def truth(w):
    """Ground truth from the checker's own asai/seer functions (all readings)."""
    def pats(x):
        try:
            return [tuple(p) for p in _readings(x)]
        except ValueError:
            return []
    g = {}
    for kind, nxt in (("c", "கண்ணம்"), ("v", "அண்ணம்")):
        ps = [p for p in pats(_elide([w, nxt])[0]) if len(p) in (2, 3) and not (len(p) == 3 and p[2] == NIRAI)]
        req = {next_start_required(p) for p in ps}
        g["next_" + kind] = 1 if NER in req else 0 if NIRAI in req else None
        g["ambiguous_" + kind] = len(req) == 2
    ps = pats(w)
    g["terminal"] = any(final_pattern(w, list(p)) for p in ps)
    g["open"] = sorted({p[0] for p in ps}) or None
    g["readings"] = [list(p) for p in ps]
    return g


def frames():
    out = {}
    for w in ("கண்ணம்", "மலரும்", "அலரும்", "அண்ணம்", "பிறவி", "உலகு", NER_PRED):
        out[f"readings[{w}]"] = [list(p) for p in _readings(w)]
    out["base frame (known-good w=கண்ணம், C-nirai probe)"] = ok(f"கண்ணம் மலரும் {TAIL}")
    out["all-மலரும் frame"] = ok(f"மலரும் மலரும் {TAIL}")
    out["NER_PRED + C-ner probe"] = ok(f"{NER_PRED} கண்ணம் {TAIL}")
    out["NER_PRED + V-ner probe"] = ok(f"{NER_PRED} அண்ணம் {TAIL}")
    out["4+3 with newline"] = ok("கண்ணம் மலரும் மலரும் மலரும்\nமலரும் மலரும் உலகு")
    out["terminal frame w=உலகு"] = ok(f"கண்ணம் {'மலரும் ' * 5}உலகு")
    out["piravi frame w=உலகு"] = ok(f"கண்ணம் {'மலரும் ' * 4}பிறவி உலகு")
    out["piravi frame w=நாள் (ner-open final)"] = ok(f"கண்ணம் {'மலரும் ' * 4}பிறவி நாள்")
    out["NER_PRED frame w=நாள்"] = ok(f"கண்ணம் {'மலரும் ' * 4}{NER_PRED} நாள்")
    return out


if __name__ == "__main__":
    print(json.dumps(frames(), ensure_ascii=False))
    d = json.load(open("data/thirukkural.json"))["kural"]
    words = collections.Counter()
    for k in d:
        for w in (k["Line1"] + " " + k["Line2"]).split():
            w = re.sub(r"[^\u0B80-\u0BFF]", "", w)
            if w:
                words[w] += 1
    ufinal = [w for w, _ in words.most_common() if w.endswith("\u0BC1")][:10]
    tricky = ["உலகு", "நன்கு", "அறிவுடையது", "எனப்படுவது", "கற்க", "அதற்குத்", "தக", "பண்புடையாளர்"] + ufinal
    for w in tricky:
        p, t = profile_v2(w), truth(w)
        mism = [k for k in ("next_c", "next_v") if p[k] != t[k]]
        if p["terminal"] != t["terminal"]: mism.append("terminal(orig)")
        if p["terminal_v2"] != t["terminal"]: mism.append("terminal_v2")
        print(json.dumps({"profile": p, "truth": t, "mismatch": mism}, ensure_ascii=False))
    t0 = time.time(); st = collections.Counter(); mm = collections.Counter(); ex = collections.defaultdict(list)
    for w in words:
        p, t = profile_v2(w), truth(w)
        st["profiled"] += 1
        st["next_c None"] += p["next_c"] is None
        st["next_v None"] += p["next_v"] is None
        st["both None"] += p["next_c"] is None and p["next_v"] is None
        st["ambiguous_c"] += p["ambiguous_c"]; st["ambiguous_v"] += p["ambiguous_v"]
        st["terminal(orig)"] += p["terminal"]; st["terminal_v2"] += p["terminal_v2"]
        st["truth terminal"] += t["terminal"]
        for k, a, b in (("next_c", p["next_c"], t["next_c"]), ("next_v", p["next_v"], t["next_v"]),
                        ("terminal(orig)", p["terminal"], t["terminal"]), ("terminal_v2", p["terminal_v2"], t["terminal"])):
            if a != b:
                mm[k] += 1; ex[k].append(w)
    dt = time.time() - t0
    print(json.dumps({"stats": st, "mismatch_vs_truth": mm, "examples": {k: v[:8] for k, v in ex.items()},
                      "seconds": round(dt, 1), "ms_per_word": round(1000 * dt / len(words), 2)}, ensure_ascii=False))
