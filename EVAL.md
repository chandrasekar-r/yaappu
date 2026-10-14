# Generation eval: unconstrained baseline vs word-level constrained decoding

Date: 2026-10-14. Hardware: CPU only (8 cores, 15 GB RAM, no GPU), bf16, torch 2.14 CPU, transformers 5.19.

## Models
- **gemma-2-2b-it via `unsloth/gemma-2-2b-it`**, an ungated mirror of the original weights. `google/gemma-2-2b-it` is gated: the box has no HF token (`hf auth whoami` says "Not logged in", and `HF_TOKEN` is unset), and its config.json returns 401.
- **Qwen/Qwen2.5-1.5B-Instruct**, a second model already in the cache.
- **gemma-2-9b-it was not run.** bf16 needs about 18 GB of RAM, which exceeds the box's 15 GB, and there is no GPU.

## Setup
- **Topics:** 20 Thirukkural chapter (adhikaram) names, evenly spaced over the 133 chapters (`data/detail.json`).
- **Prompt:** the same chat prompt for both modes: 3 fixed example kurals (1, 391, 1101) plus "write one NEW kural venba on <topic>".
- **Seeds:** gemma 3 per topic (n=60 per mode); Qwen 1 per topic (n=20 per mode).
- **Baseline:** `model.generate` with sampling (T=0.8, top-k=40, 100 new tokens); the first two non-empty lines are kept.
- **Constrained** (`yaappu/word_decode.py`), same sampling settings:
  - Only whole corpus words are allowed, and each comes with a metrical profile from `data/yaappu_profiles.json` (built by `scripts/export_profiles.py` from the black-box probe profiler `profile_v2`, and asserted to agree with the checker's own functions on all 6,347 words).
  - The words are compiled into token tries keyed by (line_start, terminal, starts_with_vowel, opening_bit). Line-start words use the bare tokenisation; mid-line words use the space-prefixed (▁/Ġ) form.
  - The decoder state carries the previous word's requirement pair (req_if_consonant, req_if_vowel), so kutriyalukaram elision before a vowel is handled. Words that can't start a Tamil word are dropped; these are the second halves of the edition's mid-word splits, e.g. லதனை.
  - The layout is fixed at 4+3, with a newline after word 4 and EOS after word 7. If no token is allowed, the decoder backtracks.
  - A `LogitsProcessor` form (`KuralWordLogitsProcessor`) is included as well.
  - Every output is re-verified with `check_kural`. The checker doesn't depend on the errata (errata only change the data). Outputs were also checked with `check_kural_licensed`.
- **Soft monai/edhugai bonus:** not implemented (optional; not done).

## Results
| model | mode | n | meter pass (check_kural) | pass (licensed checker) | 4+3 layout | distinct words / total | corpus-only vocab | copied ≥4 words of one kural | time/couplet s (mean / median) |
|---|---|---|---|---|---|---|---|---|---|
| Qwen/Qwen2.5-1.5B-Instruct | baseline | 20 | 0/20 (0%) | 0/20 (0%) | 2/20 | 146/157 | 0/20 (0%) | 0/20 | 8.9 / 8.1 |
| Qwen/Qwen2.5-1.5B-Instruct | constrained | 20 | 20/20 (100%) | 20/20 (100%) | 20/20 | 133/140 | 20/20 (100%) | 0/20 | 7.4 / 7.0 |
| unsloth/gemma-2-2b-it | baseline | 60 | 0/60 (0%) | 0/60 (0%) | 11/60 | 304/357 | 0/60 (0%) | 0/60 | 4.8 / 4.5 |
| unsloth/gemma-2-2b-it | constrained | 60 | 60/60 (100%) | 60/60 (100%) | 60/60 | 290/420 | 60/60 (100%) | 0/60 | 5.0 / 4.7 |

- "Corpus-only vocab" means every word of the output appears in the Thirukkural corpus.
- "Copied" means the output shares 4 or more words with a single real kural. No output in either mode did.
- In the baseline, the most common failures are a wrong word count and non-Tamil or non-words.
- 0 constrained outputs failed verification, and there were 0 dead ends.
- A tokenizer-free test (`tests/test_word_decode.py`) runs 200 random walks through the decoder's state machine; every finished walk passes `check_kural`.

**Limitations.**
- The constraint guarantees meter, not meaning. Outputs are grammatical-looking strings of real kural words, not coherent sentences.
- The model collapses onto some words (ஓர்ந்துகண் appears in 22/60 gemma couplets).
- No human or model judge was run.
- `results/words_*.v0_fragments.json` keeps the first run, made before fragment tokens such as லதனை and னவைநீக்கி were filtered out. Its meter scores were the same (100%).

## Reproduce
```
source /workspace/venv/bin/activate        # torch + transformers (CPU)
python scripts/export_profiles.py          # data/yaappu_profiles.json (~8 s)
python scripts/eval_words.py unsloth/gemma-2-2b-it 20 3      # ~10 min on 8 CPU cores
python scripts/eval_words.py Qwen/Qwen2.5-1.5B-Instruct 20 1  # ~6 min
python scripts/eval_words_metrics.py > results/words_metrics.md
```
`eval_words.py` is resumable: it skips (topic, mode, seed) rows that are already in `results/words_<model>.jsonl`.

## Relation to Atom's partial work (left untracked, not modified)
- `yaappu/prefix.py` and `yaappu/decode.py` implement character-level prefix constraints. Their outputs (`results/gen_*.jsonl`) scan but contain mostly non-words and empty lines.
- I reused the chapter topics and prompt from `scripts/eval_generate.py`. The decoder was replaced with the word-level one.
- Atom's job (`eval_generate.py` on Qwen-1.5B) was still running at 04:52 and was stopped to free the CPU. Its partial output is kept.
