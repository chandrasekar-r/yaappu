"""Accuracy (raw / errata) for baseline vs rule-licensed re-segmentation, plus the
shuffled-word false-accept control (same procedure and seed as scripts/bench.py).
Run: python3 scripts/bench_reseg.py"""
import sys, random, collections
sys.path.insert(0, ".")
from yaappu import check_kural
from yaappu.reseg import check_kural_licensed
from yaappu.errata import load_kurals

CHECKERS = {"baseline": check_kural, "L1": lambda t: check_kural_licensed(t, ("L1",)),
            "L1+L2": lambda t: check_kural_licensed(t, ("L1", "L2"))}


def shuffled(kurals):
    random.seed(0); out = []
    for k in kurals:
        w = (k["Line1"] + " " + k["Line2"]).split()
        if len(w) != 7:
            continue
        random.shuffle(w); out.append(" ".join(w))
    return out


raw = load_kurals("none")
neg = shuffled(raw)
print("| checker | raw | errata=typo | errata=all | shuffle false-accept |\n|---|---|---|---|---|")
for name, f in CHECKERS.items():
    cells = []
    for m in ("none", "typo", "all"):
        ks = load_kurals(m); ok = sum(f(k["Line1"] + " " + k["Line2"]).ok for k in ks)
        cells.append(f"{ok}/1330 = {100*ok/1330:.2f}%")
    fa = sum(f(t).ok for t in neg)
    print(f"| {name} | " + " | ".join(cells) + f" | {fa}/{len(neg)} = {100*fa/len(neg):.2f}% |")
print("\nRemaining failures (default L1, errata=all):")
fails = collections.defaultdict(list); rec = []
for k in load_kurals("all"):
    t = k["Line1"] + " " + k["Line2"]; r = check_kural_licensed(t)
    if not r.ok: fails[r.error].append(f"{k['Number']}: {r.detail}")
    elif not check_kural(t).ok: rec.append(f"{k['Number']} ({r.detail})")
for e, v in sorted(fails.items(), key=lambda x: -len(x[1])):
    print(f"- **{e}** ({len(v)}): " + "; ".join(v))
print(f"\nRecovered by licenses ({len(rec)}): " + "; ".join(rec))
