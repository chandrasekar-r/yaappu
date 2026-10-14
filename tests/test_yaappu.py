import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from yaappu import asai_split, check_kural, check_word


def pat(w, **kw):
    return [a for a, _ in asai_split(w, **kw)]


def test_asai():
    assert pat("அகர") == ["nirai", "ner"]
    assert pat("பார்த்தான்") == ["ner", "ner"]
    assert pat("கெடுப்பதூஉம்") == ["nirai", "nirai", "ner"]
    assert pat("கெடுப்பதூஉம்", alabedai_counts=False) == ["nirai", "nirai"]
    assert pat("தாஇல") == ["ner", "nirai"]  # long + bare vowel that is NOT alabedai


def test_kural_1():
    assert check_kural("அகர முதல எழுத்தெல்லாம் ஆதி பகவன் முதற்றே உலகு.").ok


def test_kani_rejected():
    r = check_kural("அகர முதல எழுத்தெல்லாம் ஆதி பகவன் கருவிளங்கனி உலகு")
    assert not r.ok


def test_phonotactics():
    for w in ["பார்த்தான்", "வாழ்க்கை", "காய்ந்த", "ஈர்ங்கை", "நுண்ணறிவால்", "எஃகு"]:
        assert check_word(w)[0], w
    for w in ["றண்ணக்", "லட்டு", "பார்த்த்", "வாழ்ழ்த்து", "க்த"]:
        assert not check_word(w)[0], w
    assert check_word("வான்நின்று", junctions=True)[0] and not check_word("வான்நின்று")[0]
