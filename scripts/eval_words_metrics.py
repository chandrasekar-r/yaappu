"""Metrics for results/words_*.jsonl. Usage: python3 scripts/eval_words_metrics.py"""
import glob, json, sys, re, statistics as st
sys.path.insert(0, ".")
from yaappu import check_kural
from yaappu.reseg import check_kural_licensed

P = json.load(open("data/yaappu_profiles.json"))
K = json.load(open("data/thirukkural.json"))["kural"]
KW = [set(re.sub(r"[^\u0B80-\u0BFF ]", " ", k["Line1"] + " " + k["Line2"]).split()) for k in K]
W = lambda t: re.sub(r"[^\u0B80-\u0BFF\s]", " ", t or "").split()

print("| model | mode | n | meter pass (check_kural) | pass (licensed checker) | 4+3 layout | distinct words / total | corpus-only vocab | copied ≥4 words of one kural | time/couplet s (mean / median) |")
print("|---|---|---|---|---|---|---|---|---|---|")
for f in sorted(glob.glob("results/words_*.jsonl")):
    rows = list(map(json.loads, open(f)))
    for mode in ("baseline", "constrained"):
        R = [r for r in rows if r["mode"] == mode]
        if not R: continue
        n = len(R); T = [r["text"] or "" for r in R]
        ok = sum(check_kural(t).ok for t in T if t); okl = sum(check_kural_licensed(t).ok for t in T if t)
        lay = sum(len(t.split("\n")) == 2 and [len(W(x)) for x in t.split("\n")] == [4, 3] for t in T)
        ws = [w for t in T for w in W(t)]
        corp = sum(bool(W(t)) and all(w in P for w in W(t)) for t in T)
        cp = sum(bool(W(t)) and max(len(set(W(t)) & s) for s in KW) >= 4 for t in T)
        tm = [r["time"] for r in R]
        print(f"| {R[0]['model']} | {mode} | {n} | {ok}/{n} ({100*ok/n:.0f}%) | {okl}/{n} ({100*okl/n:.0f}%) | {lay}/{n} | "
              f"{len(set(ws))}/{len(ws)} | {corp}/{n} ({100*corp/n:.0f}%) | {cp}/{n} | {st.mean(tm):.1f} / {st.median(tm):.1f} |")
