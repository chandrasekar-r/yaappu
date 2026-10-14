"""Python reference for licensed checker parity -> build/parity_lic_py.json"""
import sys, json, random
sys.path.insert(0, "..")
from yaappu.reseg import check_kural_licensed
from yaappu.errata import load_kurals, normalize
texts = []
for m in ("none", "typo", "all"):
    texts += [k["Line1"] + "\n" + k["Line2"] for k in load_kurals(m)]
P = json.load(open("../data/sources/parimelazhagar_wikisource.json")); texts += [v["poem"] for v in P.values()]
random.seed(1)
for t in texts[:1330]:
    w = t.split(); random.shuffle(w); texts.append(" ".join(w))
    i = random.randrange(len(t)); texts.append(t[:i] + t[i + 1:])
out = []
for t in texts:
    r = check_kural_licensed(t)
    out.append({"text": t, "ok": r.ok, "error": r.error, "detail": r.detail, "seers": r.seers, "norm": normalize(t)})
json.dump(out, open("build/parity_lic_py.json", "w"), ensure_ascii=False)
print(len(out), sum(o["ok"] for o in out[1330:2660]), "typo-errata ok")
