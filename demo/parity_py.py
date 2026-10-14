"""Dump Python check_kural results for the parity set -> demo/build/parity_py.json"""
import sys, json, random
sys.path.insert(0, ".")
from yaappu import check_kural
from yaappu.errata import load_kurals
texts = []
for m in ("none", "typo", "all"):
    texts += [k["Line1"] + "\n" + k["Line2"] for k in load_kurals(m)]
raw = texts[:1330]
random.seed(1)
for t in raw:                       # shuffled words + one random character deleted
    w = t.split(); random.shuffle(w); texts.append(" ".join(w))
    i = random.randrange(len(t)); texts.append(t[:i] + t[i + 1:])
out = []
for t in texts:
    r = check_kural(t)
    out.append({"text": t, "ok": r.ok, "error": r.error, "detail": r.detail, "seers": r.seers})
json.dump(out, open("demo/build/parity_py.json", "w"), ensure_ascii=False)
print(len(out), "cases;", sum(o["ok"] for o in out), "ok")
