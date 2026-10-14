"""Tokenizer-free test of the word-trie decoder state machine (fake whitespace tokenizer)."""
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from yaappu.word_decode import WordTries, Cursor
from yaappu import check_kural


class FakeTok:
    """Character-level 'tokenizer': ids are code points; ' ' prefixes mark mid-line forms."""
    eos_token_id = 0
    def encode(self, s, add_special_tokens=False): return [ord(c) for c in s]
    def decode(self, ids): return "".join(chr(i) for i in ids)
    def get_vocab(self): return {}


def test_random_walks_always_scan():
    T = WordTries(FakeTok()); rng = random.Random(0); done = 0
    for _ in range(200):
        c = Cursor(T)
        for _ in range(300):
            acts = c.allowed()
            if not acts: break
            t = rng.choice(list(acts)); c.step(t, acts)
            if c.slot == 7: break
        if c.slot == 7:
            done += 1
            assert check_kural(c.text()).ok, c.text()
            assert [len(l.split()) for l in c.text().split("\n")] == [4, 3]
    assert done > 150
