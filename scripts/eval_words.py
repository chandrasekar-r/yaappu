"""Baseline (unconstrained) vs word-level constrained kural generation.
Usage: python scripts/eval_words.py MODEL [N_TOPICS=20] [SEEDS=1]
Writes results/words_<model>.jsonl (resumable)."""
import sys, json, os, time, torch
sys.path.insert(0, ".")
from transformers import AutoTokenizer, AutoModelForCausalLM
from yaappu.word_decode import WordTries, generate

MODEL = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 20
SEEDS = int(sys.argv[3]) if len(sys.argv) > 3 else 1
torch.set_num_threads(8)
K = json.load(open("data/thirukkural.json"))["kural"]
det = json.load(open("data/detail.json"))[0]["section"]["detail"]
CH = [c for p in det for g in p["chapterGroup"]["detail"] for c in g["chapters"]["detail"]]
TOPICS = [CH[i * len(CH) // N] for i in range(N)]
SHOTS = (0, 390, 1100)


def prompt(tok, topic):
    shots = "\n\n".join(K[i]["Line1"] + "\n" + K[i]["Line2"] for i in SHOTS)
    msg = ("You are a classical Tamil poet. Reply with exactly one new Kural Venba in Tamil script "
           "(two lines: 4 words, then 3 words) and nothing else.\n\nExample kurals:\n\n" + shots +
           f"\n\nWrite one NEW kural venba (do not copy) on the topic: {topic['name']} ({topic['translation']}).")
    return tok.apply_chat_template([{"role": "user", "content": msg}], add_generation_prompt=True,
                                   return_tensors="pt", return_dict=True)["input_ids"]


def main():
    os.makedirs("results", exist_ok=True)
    path = f"results/words_{MODEL.split('/')[-1]}.jsonl"
    done = {(r["topic_no"], r["mode"], r["seed"]) for r in map(json.loads, open(path))} if os.path.exists(path) else set()
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16).eval()
    t = time.time(); T = WordTries(tok); print(f"tries built in {time.time()-t:.1f}s", flush=True)
    with open(path, "a") as f:
        for n, tp in enumerate(TOPICS):
            ids = prompt(tok, tp)
            for s in range(SEEDS):
                seed = 1000 * s + n
                for mode in ("baseline", "constrained"):
                    if (tp["number"], mode, seed) in done:
                        continue
                    if mode == "baseline":
                        torch.manual_seed(seed); t0 = time.time()
                        with torch.no_grad():
                            out = model.generate(ids, max_new_tokens=100, do_sample=True, temperature=0.8, top_k=40)
                        txt = tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True)
                        txt = "\n".join([l.strip() for l in txt.splitlines() if l.strip()][:2])
                        info = {"time": time.time() - t0, "tokens": out.shape[1] - ids.shape[1], "status": "ok"}
                    else:
                        txt, info = generate(model, T, ids, seed=seed)
                    rec = {"topic_no": tp["number"], "topic": tp["name"], "mode": mode, "seed": seed, "model": MODEL, "text": txt, **info}
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
                    print(n, mode, info["status"], round(info["time"], 1), (txt or "").replace("\n", " / "), flush=True)


if __name__ == "__main__":
    main()
