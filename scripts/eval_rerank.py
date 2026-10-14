"""Part A: constrained decoding with no-repeat + frequency penalty, N candidates per topic,
reranked by the model's own mean log-prob of the couplet under a coherence prompt, plus a
soft monai/edhugai bonus. Usage: python scripts/eval_rerank.py [N_TOPICS=20] [N_CAND=8]
Writes results/rerank_gemma-2-2b-it.jsonl (all candidates, with scores; chosen=True on the winner)."""
import sys, json, os, time, collections, torch
sys.path.insert(0, ".")
from transformers import AutoTokenizer, AutoModelForCausalLM
from yaappu.word_decode import WordTries, generate
from yaappu import check_kural
from yaappu.graphemes import parse
sys.argv += [] ; sys.path.insert(0, "scripts")
import eval_words as E

MODEL = "unsloth/gemma-2-2b-it"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20
NC = int(sys.argv[2]) if len(sys.argv) > 2 else 8
ALPHA, BETA = 1.5, 0.15   # frequency penalty per previous use (logits); bonus per monai/edhugai match (nats/token)
torch.set_num_threads(8)


def monai_edhugai(text):
    """Soft count: monai = first letter (consonant or vowel) of seer1 recurs at seer3 / seer5 head;
    edhugai = second grapheme's consonant of line-1 and line-2 first words match."""
    w = text.split()
    g = [parse(x) for x in w]
    head = lambda gs: gs[0].cons or gs[0].vowel
    m = sum(head(g[0]) == head(g[k]) for k in (2, 4))
    e = int(len(g[0]) > 1 and len(g[4]) > 1 and g[0][1].cons is not None and g[0][1].cons == g[4][1].cons)
    return m, e


@torch.no_grad()
def coherence_logprob(model, tok, topic, text):
    msg = f"Write one meaningful, grammatical classical Tamil couplet (kural) about: {topic['name']} ({topic['translation']})."
    pre = tok.apply_chat_template([{"role": "user", "content": msg}], add_generation_prompt=True, return_tensors="pt", return_dict=True)["input_ids"]
    tgt = tok(text, add_special_tokens=False, return_tensors="pt")["input_ids"]
    ids = torch.cat([pre, tgt], 1)
    lp = torch.log_softmax(model(ids).logits[0, pre.shape[1] - 1:-1].float(), -1)
    return lp.gather(1, tgt[0][:, None]).mean().item()


def main():
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16).eval()
    T = WordTries(tok)
    topics = [E.CH[i * len(E.CH) // N] for i in range(N)]
    used = collections.Counter()
    path = "results/rerank_gemma-2-2b-it.jsonl"
    with open(path, "w") as f:
        for n, tp in enumerate(topics):
            ids = E.prompt(tok, tp); cands = []; t0 = time.time()
            for c in range(NC):
                pen = {w: ALPHA * k for w, k in used.items()}
                for w in [x for cc in cands for x in cc["text"].split()]:
                    pen[w] = pen.get(w, 0) + ALPHA   # diversity across this topic's candidates too
                txt, info = generate(model, T, ids, seed=10000 + 100 * n + c, no_repeat=True, word_penalty=pen)
                if not txt:
                    continue
                lp = coherence_logprob(model, tok, tp, txt)
                m, e = monai_edhugai(txt)
                cands.append({"text": txt, "gen_time": info["time"], "status": info["status"], "coh_lp": lp,
                              "monai": m, "edhugai": e, "score": lp + BETA * (m + e)})
            best = max(cands, key=lambda r: r["score"])
            used.update(best["text"].split())
            el = time.time() - t0
            for r in cands:
                rec = {"topic_no": tp["number"], "topic": tp["name"], "model": MODEL, **r, "chosen": r is best,
                       "topic_time": el, "meter_ok": check_kural(r["text"]).ok}
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            print(n, round(el, 1), round(best["score"], 3), best["text"].replace("\n", " / "), flush=True)


if __name__ == "__main__":
    main()
