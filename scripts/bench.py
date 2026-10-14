"""Benchmark: meter checker on all 1,330 kurals + phonotactic false-rejection rate."""
import json, collections, sys
sys.path.insert(0, ".")
from yaappu import check_kural
from yaappu.phonotactics import check_text

d = json.load(open("data/thirukkural.json"))["kural"]


def data_suspect(text):
    """Heuristic flag for transcription errors in the source edition."""
    if "\u0BC6ள" in text or any(not ("\u0B80" <= c <= "\u0BFF" or c in " .,?") for c in text):
        return True
    bad = [w for w, ok, why in check_text(text, True) if not ok and "cluster" in why and not why.endswith("\u0BCD")]
    return bool(bad)


fails = collections.defaultdict(list); ok = 0
for k in d:
    t = k["Line1"] + " " + k["Line2"]
    r = check_kural(t)
    if r.ok: ok += 1
    else: fails["source typo (suspected)" if data_suspect(t) else r.error].append((k["Number"], r.detail))
print(f"## Meter: {ok}/{len(d)} = {100*ok/len(d):.2f}% pass\n")
for e, v in sorted(fails.items(), key=lambda x: -len(x[1])):
    print(f"- **{e}** ({len(v)}): " + "; ".join(f"{n}: {x}" for n, x in v))
for J in (False, True):
    rej = collections.Counter(); ex = collections.defaultdict(list); total = 0
    for k in d:
        for w, good, why in check_text(k["Line1"] + " " + k["Line2"], J):
            total += 1
            if not good:
                rej[why] += 1; ex[why].append(w)
    bad = sum(rej.values())
    print(f"\n## Phonotactics (unsandhied-compound junctions {'allowed' if J else 'strict'}): "
          f"{bad}/{total} words rejected = {100*bad/total:.2f}%\n")
    for key, v in rej.most_common(10): print(f"- {key} ({v}): {', '.join(ex[key][:4])}")

# --- robustness / ablations -------------------------------------------------
import random
import yaappu.venba as V
random.seed(0); acc = n = 0
for k in d:
    w = (k["Line1"] + " " + k["Line2"]).split()
    if len(w) != 7:
        continue
    random.shuffle(w); n += 1; acc += check_kural(" ".join(w)).ok
print(f"\n## Shuffle test (word order randomised, seed 0): {acc}/{n} = {100*acc/n:.1f}% still accepted")
V.ELIDE = False
noel = sum(check_kural(k["Line1"] + " " + k["Line2"]).ok for k in d)
V.ELIDE = True
print(f"\n## Ablation: kutriyalukaram elision off: {noel}/{len(d)} = {100*noel/len(d):.2f}% "
      f"(full rule set: {ok}/{len(d)} = {100*ok/len(d):.2f}%)")
