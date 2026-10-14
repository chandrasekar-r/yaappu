"""Meaningfulness proxy: perplexity of the plain couplet text (no prompt) under an
independent LM (Qwen2.5-3B-Instruct, not used for generation or reranking).
Lower = more LM-plausible Tamil. Also scores 60 real kurals as a reference.
Usage: python scripts/eval_ppl_words.py -> results/ppl_words.json and a markdown table."""
import sys, json, math, statistics as st, torch, random
sys.path.insert(0, ".")
from transformers import AutoTokenizer, AutoModelForCausalLM
from yaappu import check_kural
M = "Qwen/Qwen2.5-3B-Instruct"; torch.set_num_threads(8)
tok = AutoTokenizer.from_pretrained(M); model = AutoModelForCausalLM.from_pretrained(M, dtype=torch.bfloat16).eval()


@torch.no_grad()
def ppl(t):
    ids = tok(t, return_tensors="pt")["input_ids"]
    ids = torch.cat([torch.tensor([[tok.convert_tokens_to_ids("<|endoftext|>")]]), ids], 1)
    lp = torch.log_softmax(model(ids).logits[0, :-1].float(), -1).gather(1, ids[0, 1:, None])
    return math.exp(-lp.mean().item())


sets = {}
W = [json.loads(l) for l in open("results/words_gemma-2-2b-it.jsonl")]
sets["baseline (gemma, n=60)"] = [r["text"] for r in W if r["mode"] == "baseline" and r["text"]]
sets["constrained before (gemma, n=60)"] = [r["text"] for r in W if r["mode"] == "constrained"]
RR = [json.loads(l) for l in open("results/rerank_gemma-2-2b-it.jsonl")]
sets["constrained after: all candidates"] = [r["text"] for r in RR]
sets["constrained after: reranked winners (n=20)"] = [r["text"] for r in RR if r["chosen"]]
K = json.load(open("data/thirukkural.json"))["kural"]; random.seed(0)
sets["real Thirukkural (random 60)"] = [k["Line1"] + "\n" + k["Line2"] for k in random.sample(K, 60)]
out = {}
print("| set | n | meter pass | PPL median | PPL mean |\n|---|---|---|---|---|")
for name, T in sets.items():
    P = [ppl(t) for t in T]; out[name] = P
    ok = sum(check_kural(t).ok for t in T)
    print(f"| {name} | {len(T)} | {ok}/{len(T)} | {st.median(P):.0f} | {st.mean(P):.0f} |", flush=True)
json.dump(out, open("results/ppl_words.json", "w"))
