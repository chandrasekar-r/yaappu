"""Word-level constrained Kural Venba decoding over corpus vocabulary.

Every generated word is a whole corpus word with a metrical profile
(data/yaappu_profiles.json). Words are compiled into token tries keyed by
(line_start, terminal, starts_with_vowel, opening_bit); line-start words use the
bare tokenisation, mid-line words the space-prefixed (▁ / Ġ) form. The decoder
state carries the previous word's requirement pair (req_if_consonant,
req_if_vowel): the next word must open with an asai in the set selected by its
own initial letter. Layout is fixed at 4+3 (newline after word 4, EOS after
word 7). The result is re-verified with check_kural; a failure is reported,
never silently accepted.

`KuralWordLogitsProcessor` exposes the same masking as a transformers
LogitsProcessor (for model.generate); `generate` is the KV-cached sampler used
by the eval (identical masks, plus dead-end backtracking).
"""
import json, os, time, collections
import torch
from transformers import LogitsProcessor

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NER, NIRAI = "ner", "nirai"


class Node:
    __slots__ = ("kids", "word")

    def __init__(self):
        self.kids, self.word = {}, None


def _insert(root, ids, w):
    n = root
    for i in ids:
        n = n.kids.setdefault(i, Node())
    if n.word is None:
        n.word = w


class WordTries:
    def __init__(self, tok, profiles=None, min_freq=1, phonotactic=True):
        """phonotactic=True drops corpus tokens that cannot start a word (the second halves
        of the edition's mid-word seer splits, e.g. லதனை, னவைநீக்கி), via phonotactics.check_word."""
        from .phonotactics import check_word
        P = profiles or json.load(open(os.path.join(_ROOT, "data", "yaappu_profiles.json")))
        self.P = {w: p for w, p in P.items() if p["freq"] >= min_freq
                  and (not phonotactic or check_word(w, junctions=True)[0])}
        self.tok = tok
        self.tries = collections.defaultdict(Node)
        for w, p in self.P.items():
            sv = p["starts_with_vowel"]
            forms = {True: tok.encode(w, add_special_tokens=False),
                     False: tok.encode(" " + w, add_special_tokens=False)}
            for ls, ids in forms.items():
                if tok.decode(ids).strip() != w:  # tokenisation must round-trip
                    continue
                if p["next_req_if_c"] or p["next_req_if_v"]:
                    for ob in p["opening_bits"]:
                        _insert(self.tries[(ls, False, sv, ob)], ids, w)
                if p["terminal"]:
                    for ob in p["terminal_open"]:
                        _insert(self.tries[(ls, True, sv, ob)], ids, w)
        nl = tok.encode("\n", add_special_tokens=False)
        assert len(nl) == 1, nl
        self.nl = nl[0]
        eos = {tok.eos_token_id}
        for t in ("<end_of_turn>", "<|im_end|>"):
            if t in tok.get_vocab():
                eos.add(tok.convert_tokens_to_ids(t))
        self.eos = sorted(e for e in eos if e is not None)

    def roots(self, slot, req):
        """Trie roots allowed at `slot` (0..6) given the previous word's (req_c, req_v)."""
        ls, term = slot in (0, 4), slot == 6
        if req is None:
            return [self.tries[(ls, term, sv, ob)] for sv in (False, True) for ob in (NER, NIRAI)]
        rc, rv = req
        return [self.tries[(ls, term, False, ob)] for ob in rc] + [self.tries[(ls, term, True, ob)] for ob in rv]

    def req(self, w):
        p = self.P[w]
        return (p["next_req_if_c"], p["next_req_if_v"])


class Cursor:
    """Decoder state: slot, previous requirement, active trie nodes, words so far."""

    def __init__(self, T):
        self.T, self.slot, self.words, self.nodes, self.pending_sep = T, 0, [], T.roots(0, None), None

    def allowed(self):
        """token id -> action list. Actions: ('in', nodes) | ('next', w, nodes) | ('sep', w) | ('eos', w)."""
        if self.pending_sep is not None:
            return {self.pending_sep: [("after_sep",)]}
        acts = collections.defaultdict(list)
        for n in self.nodes:
            for t, k in n.kids.items():
                acts[t].append(("in", k))
        done = [n.word for n in self.nodes if n.word]
        for w in dict.fromkeys(done):
            if self.slot == 6:
                for e in self.T.eos:
                    acts[e].append(("eos", w))
            elif self.slot == 3:
                acts[self.T.nl].append(("sep", w))
            else:
                for r in self.T.roots(self.slot + 1, self.T.req(w)):
                    for t, k in r.kids.items():
                        acts[t].append(("next", w, k))
        return acts

    def step(self, t, acts):
        a = acts[t]
        if a[0][0] == "after_sep":
            self.pending_sep = None; return
        nxt = [x for x in a if x[0] == "next"]
        if nxt:
            w = nxt[0][1]
            self.words.append(w); self.slot += 1
            self.nodes = [x[2] for x in nxt if x[1] == w]
        elif a[0][0] == "sep":
            self.words.append(a[0][1]); self.slot += 1
            self.nodes = self.T.roots(4, self.T.req(a[0][1]))
        elif a[0][0] == "eos":
            self.words.append(a[0][1]); self.slot = 7
        else:
            self.nodes = [x[1] for x in a]

    def text(self):
        w = self.words
        return " ".join(w[:4]) + ("\n" + " ".join(w[4:]) if len(w) > 4 else "")


class KuralWordLogitsProcessor(LogitsProcessor):
    """Batch-1 LogitsProcessor version: replays the generated suffix through a Cursor."""

    def __init__(self, T, prompt_len):
        self.T, self.p = T, prompt_len

    def __call__(self, input_ids, scores):
        c = Cursor(self.T)
        for t in input_ids[0, self.p:].tolist():
            c.step(t, c.allowed())
        out = torch.full_like(scores, float("-inf"))
        ids = list(c.allowed())
        if ids:
            out[0, ids] = scores[0, ids]
        return out


@torch.no_grad()
def generate(model, T, prompt_ids, temperature=0.8, top_k=40, seed=0, max_steps=200, max_backtracks=100):
    import copy
    from .venba import check_kural
    g = torch.Generator().manual_seed(seed); t0 = time.time()
    o = model(prompt_ids, use_cache=True)
    cache = o.past_key_values
    stack = [(Cursor(T), o.logits[0, -1])]
    gen, banned, bt, steps = [], collections.defaultdict(set), 0, 0
    while steps < max_steps:
        steps += 1
        cur, logits = stack[-1]
        if cur.slot == 7:
            txt = cur.text()
            return txt, {"time": time.time() - t0, "tokens": len(gen), "backtracks": bt,
                         "status": "ok" if check_kural(txt).ok else "verify_failed"}
        acts = cur.allowed()
        ids = [i for i in acts if i not in banned[len(gen)]]
        if not ids:
            if not gen or bt >= max_backtracks:
                return None, {"time": time.time() - t0, "tokens": len(gen), "backtracks": bt, "status": "dead_end"}
            bt += 1; banned.pop(len(gen), None); banned[len(gen) - 1].add(gen.pop()); stack.pop(); cache.crop(-1)
            continue
        lg = logits[torch.tensor(ids)].float()
        if len(ids) > top_k:
            keep = torch.topk(lg, top_k).indices; ids = [ids[i] for i in keep.tolist()]; lg = lg[keep]
        pr = torch.softmax(lg / temperature, -1)
        t = ids[torch.multinomial(pr, 1, generator=g).item()]
        nc = copy.copy(cur); nc.words = list(cur.words); nc.step(t, acts)
        gen.append(t)
        o = model(torch.tensor([[t]]), past_key_values=cache, use_cache=True)
        cache = o.past_key_values
        stack.append((nc, o.logits[0, -1]))
    return None, {"time": time.time() - t0, "tokens": len(gen), "backtracks": bt, "status": "max_steps"}
