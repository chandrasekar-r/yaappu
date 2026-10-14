"""Source errata (data/errata.json) applied on load; raw data is never modified."""
import json, os, re

_PKG = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_PKG)


def _data(name):
    """Repo checkout: data/<name>; installed package: yaappu/data/<name> (bundled copy)."""
    p = os.path.join(_ROOT, "data", name)
    return p if os.path.exists(p) else os.path.join(_PKG, "data", name)
_AU = re.compile("\u0BC6\u0BB3(?![\u0BBE-\u0BCD\u0BD7])")  # ெ + bare ள  ->  ௌ


def normalize(text: str) -> str:
    return _AU.sub("\u0BCC", text)


def load_errata(path=None):
    return json.load(open(path or _data("errata.json")))


def load_kurals(errata: str = "none", path=None):
    """errata: 'none' (raw), 'typo' (normalisation + verified typo fixes),
    'all' (also editorial re-segmentations taken from the same verified source)."""
    d = json.load(open(path or _data("thirukkural.json")))["kural"]
    out = [dict(k) for k in d]
    if errata == "none":
        return out
    fixes = {e["number"]: e for e in load_errata()["entries"] if errata == "all" or e["type"] == "typo"}
    for k in out:
        e = fixes.get(k["Number"])
        if e:
            assert (k["Line1"], k["Line2"]) == (e["raw"]["Line1"], e["raw"]["Line2"]), k["Number"]
            k["Line1"], k["Line2"] = e["corrected"]["Line1"], e["corrected"]["Line2"]
        k["Line1"], k["Line2"] = normalize(k["Line1"]), normalize(k["Line2"])
    return out
