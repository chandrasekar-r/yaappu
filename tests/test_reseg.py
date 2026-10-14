import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from yaappu import check_kural
from yaappu.reseg import check_kural_licensed
from yaappu.errata import load_kurals, normalize


def text(ks, n):
    k = ks[n - 1]; assert k["Number"] == n
    return k["Line1"] + " " + k["Line2"]


def test_raw_data_untouched():
    raw = json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "thirukkural.json")))["kural"]
    assert load_kurals("none") == raw
    assert "கெளவை" in text(load_kurals("none"), 1143)


def test_au_normalisation():
    assert normalize("கெளவை") == "கௌவை"
    assert normalize("தெளிவு") == "தெளிவு" and normalize("வெள்ளம்") == "வெள்ளம்"
    assert check_kural(text(load_kurals("typo"), 1143)).ok


def test_errata_levels():
    assert check_kural(text(load_kurals("typo"), 154)).ok          # பொற்யுடைமை -> பொறையுடைமை
    assert text(load_kurals("typo"), 93) == text(load_kurals("none"), 93)  # segmentation not in 'typo'
    assert check_kural(text(load_kurals("all"), 93)).ok


def test_kutriyalikaram_license():
    raw = load_kurals("none")
    for n in (178, 291, 844, 1041, 1299):                          # -து/-கு + ய, and editorial "தியா"
        assert not check_kural(text(raw, n)).ok
        r = check_kural_licensed(text(raw, n))
        assert r.ok and "L1" in r.detail, n


def test_license_does_not_rescue_shuffles():
    assert not check_kural_licensed("உலகு அகர முதல ஆதி பகவன் எழுத்தெல்லாம் முதற்றே").ok


def test_parimelazhagar_errata_levels():
    from yaappu.reseg import check_kural_licensed
    typo, allk = load_kurals("typo"), load_kurals("all")
    for n in (114, 434, 719, 858, 882):              # word-level typos, verified in the Parimelazhagar edition
        assert check_kural_licensed(text(typo, n)).ok, n
    for n in (4, 170, 278, 738, 764, 1134, 1249):   # variants / edition seer division: 'all' only
        assert text(typo, n) == text(load_kurals("none"), n) or n in ()
        assert check_kural_licensed(text(allk, n)).ok, n
    fails = [k["Number"] for k in allk if not check_kural_licensed(k["Line1"] + "\n" + k["Line2"]).ok]
    assert fails == [778, 832], fails


def test_bundled_data_in_sync():
    root = os.path.join(os.path.dirname(__file__), "..")
    for f in ("thirukkural.json", "errata.json"):
        assert open(os.path.join(root, "data", f), "rb").read() == open(os.path.join(root, "yaappu", "data", f), "rb").read(), f
