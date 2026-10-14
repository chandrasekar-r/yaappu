# yaappu: Tamil kural venba prosody (யாப்பு)

**Live demo: https://yaappu.rclabs.in**

yaappu is a rule-based Tamil meter toolkit. It includes:
- a kural venba checker covering asai, seer, venthalai, the final seer, kutriyalukaram elision, resyllabification and licensed kutriyalikaram;
- a Mozhimarapu phonotactic filter;
- a word-level constrained decoder that makes a language model write couplets that always scan.

```python
from yaappu import check_kural
from yaappu.reseg import check_kural_licensed
check_kural("அகர முதல எழுத்தெல்லாம் ஆதி\nபகவன் முதற்றே உலகு.").seers
# ['புளிமா', 'புளிமா', 'புளிமாங்காய்', 'தேமா', 'புளிமா', 'புளிமா', 'பிறப்பு']
```

## Results (all 1,330 Thirukkural couplets)

| checker | raw text | errata = typo | errata = all | shuffled-word false accepts |
|---|---|---|---|---|
| base (`check_kural`) | 1284 (96.54%) | 1306 (98.20%) | 1318 (99.10%) | 14/1305 |
| licensed (`check_kural_licensed`, L1 kutriyalikaram) | 1294 (97.29%) | 1316 (98.95%) | **1328 (99.85%)** | 14/1305 |

- **Errata:** `data/errata.json`, applied with `yaappu.errata.load_kurals("typo" | "all")`. The raw data is never modified.
- **Sources:** every correction cites a Tamil Wikisource edition: *திருக்குறள், மூலம்* or *திருக்குறள் பரிமேலழகர் உரை*. Each entry records the page URL, the revision id and the exact line. `all` adds variant readings and the edition's seer division (vakaiyuli).
- **Two kurals still fail:** 778 and 832 fail in both editions. They are left failing rather than forced through with an exception; see [BENCHMARK.md](BENCHMARK.md).
- **Constrained generation (gemma-2-2b-it, CPU):** 60/60 couplets pass the meter checker, against 0/60 for the unconstrained baseline. The constraint guarantees meter, not meaning. See [EVAL.md](EVAL.md).
- **TypeScript port** (`demo/src/checker.ts`, `licensed.ts`): matches the Python output exactly on 7,941 test cases.

## Layout
- `yaappu/`: the package. `graphemes`, `asai`, `venba` (checker), `reseg` (licensed re-segmentation), `errata`, `phonotactics`, `word_decode` (constrained decoder; needs torch and transformers).
- `scripts/`:
  - `bench.py`, `bench_reseg.py`: checker benchmarks.
  - `probe_profiler.py`, `export_profiles.py`: word profiles.
  - `eval_words.py`, `eval_rerank.py`, `eval_ppl_words.py`, `eval_words_metrics.py`: generation eval.
- `demo/`: the Cloudflare Worker behind yaappu.rclabs.in, plus parity scripts and screenshots.
- `tests/`: run `python -m pytest`.

## Install
```
pip install yaappu            # core checker, no dependencies
pip install "yaappu[decode]"  # constrained decoder (torch, transformers)
```

## Data and licences
- **Code:** MIT (see LICENSE).
- **`data/thirukkural.json`, `data/detail.json`:** from [tk120404/thirukkural](https://github.com/tk120404/thirukkural), Apache-2.0.
- **`data/sources/parimelazhagar_wikisource.json` and the cited readings in `data/errata.json`:** from Tamil Wikisource, CC BY-SA 4.0.
