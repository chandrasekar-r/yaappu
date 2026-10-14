# yaappu — follow-on plan (re-segmentation, demo, paper)

Scope note: the constrained decoder and the baseline-vs-constrained eval (EVAL.md) belong to another worker. Nothing here touches decoder files. The only new code is `scripts/reseg_search.py`, a standalone prototype that imports `yaappu/` read-only.

## 1. Seer re-segmentation search (target: >98%, i.e. ≥1304/1330)

### 1.1 Failure taxonomy (46 failures in BENCHMARK.md, baseline 1284/1330 = 96.54%)

| Class | n | Root cause | Fix | Est. recovered |
|---|---|---|---|---|
| thalai: seer ≠ word, editorial split (e.g. 775 `வேல்கொண டெறிய`, 114 `காணப் படும்`, 254 `அருளல்ல தியாதெனிற்`, 844, 882) | ~6 | The edition already splits words mid-word, and the split doesn't match the metrical seer | boundary shift by 1–2 graphemes | 4–6 |
| thalai: glide/puṇarchi at a vowel–vowel junction (4 `வேண்டாமை இலானடி`, 278, 39, 778, 1134, 1249, 360) | ~7 | Sandhi across the boundary (உடம்படுமெய் y/v, a consonant moving onto the next vowel) changes where the seer cuts | sandhi-licensed shift | 3–5 |
| thalai: kutriyalukaram/aytham edge cases (170 `அஃத்இல்லார்`, 653 `ஒஓதல்`, 719, 738) | ~4 | elision and alabedai readings not tried in every combination | extend `_readings` (alabedai on the initial vowel, aytham as ner) | 2–3 |
| source typo (154, 599, 855, 858, 1143, 1147, 1148, 1150) | 8 | `கெளவை` is written with ெ+ள where it should be ௌ (4 kurals); `க்லூ` and `ற்யு` are transcription errors | normalise ௌ, then diff against a second edition (Project Madurai) | 6–8 |
| seer_length (93, 178, 287, 585, 832, 895, 1299) | 7 | 4-asai or 1-asai words that the scansion has to split or join | shift/split search | 3–5 |
| kani_seer (98, 291, 324, 795, 801, 1041) | 6 | `எனப்படுவது` ×3 needs elision of the final u (ப்படுவ(து) before a vowel); 98 `சிறுமையுவு` looks like a typo | elision before a vowel-initial word, plus typo fix | 3–5 |
| word_count (42, 689, 976, 1117) | 4 | tokens have to be split or merged | 6→7 split, 8→7 merge plus shift; 1117 has a duplicated `க்குப்` token (data) | 2–3 |
| unscannable (434, 651: leading consonant) | 2 | stray pulli or a split at a consonant | data fix or merge with the previous word | 1–2 |
| final_seer (269) | 1 | `டவர்க்குல்.` is likely a typo | data | 0–1 |
| **Total** | 46 | | | **~24–38 → 98.3–99.4%** |

### 1.2 Prototype measured (`scripts/reseg_search.py`)

Algorithm: run this only when the baseline rejects the line. Flatten the 7 seer-candidate tokens into one grapheme stream, after elision and the 8→7 merge or 6→7 split. Each of the 6 internal boundaries may move by up to K graphemes. A cut may not land before a pure consonant (mei). Candidates are enumerated in order of total shift cost, so the smallest change comes first. Each candidate is scanned with the existing `_readings` and `_check_combo`, and the first one that scans is accepted.

| K | Recovered | Accuracy | False-accept on 394 shuffled lines that the baseline rejects |
|---|---|---|---|
| 0 (baseline) | — | 1284/1330 = 96.54% | — |
| 1 | +7 | 1291/1330 = **97.07%** | 7 (1.8%) |
| 2 | +17 | 1301/1330 = **97.82%** | 30 (7.6%) |

Run time is about 10 s per setting. Run it with `python3 scripts/reseg_search.py 2`.

What the numbers show:
- Unconstrained shifting gets close to 98% but **does not reach it**, and it has two problems:
  - The negative control shows it becomes permissive at K=2.
  - Some recoveries are linguistically bogus. 93 has cost 6 and lands on `அமர்ந்த்இ`; 114 produces `என்பத்`; 154 and 855 "pass" on source typos.
- Accept only cost ≤ 2 shifts where the cut follows a vowel or a sandhi site.

### 1.3 Design for the production version (target: ≥98% with false-accept ≤1%)

1. **Data first (≈ +8):**
   - Normalise `ெள` to `ௌ` (4 kurals: 1143, 1147, 1148, 1150).
   - Cross-check the 12 suspect kurals (154, 599, 855, 858, 98, 1117, 269, 434, 651, …) against a second source, e.g. the Project Madurai Thirukkural.
   - Record every fix in `data/ERRATA.md`. Don't silently change the benchmark: report the results on both the raw and the corrected text.
2. **Licensed shifts only:** a seer boundary may move off a word boundary only when one of these holds:
   - (a) the edition already split a word mid-word (a token without a lexicon match, e.g. `டெறிய`, `தியாதெனிற்`);
   - (b) consonant-final + vowel-initial puṇarchi (the existing `_resyllabify`, generalised to a shift of 2);
   - (c) vowel + vowel with a y/v glide inserted (உடம்படுமெய்);
   - (d) kutriyalukaram elision.
   
   Each license has a cost. The search stays a best-first/Dijkstra-style enumeration over cut vectors, at most 5^6 states, about 10 ms per line.
3. **Readings:** extend `_readings` to cover `எனப்படுவது`-type elision before a vowel and to read a word-initial short vowel after a long vowel as alabedai (653 `ஒஓதல்`).
4. **Acceptance test:**
   - Accuracy on raw text and on corrected text.
   - False-accept rate on 3 negative sets: shuffled words, a random one-grapheme deletion per line, and asiriyappa lines.
   - Gate: ≥98% on corrected text and ≤1% false-accept.
   - Also emit the chosen segmentation, so the result can be checked by hand against a commentary (Parimelazhagar).
5. Estimate: data fixes (+6–8) plus licensed shifts (+10–14) plus readings (+3–5) gives 1303–1311, about **98.0–98.6%**.

## 2. Demo: yaappu.rclabs.in (Cloudflare Worker), not deployed yet

- **What it shows:**
  - (a) A **checker**. Paste a kural and get a grapheme→asai→seer table, the venthalai links coloured pass/fail, the failure class and a suggested fix. The re-segmented reading is shown as a diff.
  - (b) A **browser of the 1,330 kurals**, with pass/fail filters and the benchmark stats.
  - (c) A **phonotactic filter view**: highlight the clusters that get rejected.
  - (d) Later, **generation** side by side: baseline vs constrained. This uses the other worker's decoder and EVAL.md numbers and is read-only, from precomputed samples, until a live inference backend is chosen.
- **Stack:**
  - Port the checker to TypeScript. It's about 400 lines of pure logic and the grapheme tables are small.
  - Golden tests: run all 1,330 kurals through Python and TS and require identical output.
  - Worker plus static assets (Workers Static Assets), using Hono or plain fetch. No database: the kural JSON and precomputed results are bundled. Endpoints: `GET /api/kural/:n` and `POST /api/check`.
  - Alternative to the port: Pyodide in the browser. Faster to ship, but about 10 MB to load. Prefer the TS port.
- **Hosting:**
  - `wrangler deploy` with a custom domain route `yaappu.rclabs.in`. This needs the rclabs.in zone to be on the connected Cloudflare account; check with whoami/zone listing before deploying.
  - Live generation, if it's added later, goes through a separate backend (Railway or Workers AI) behind `/api/generate` with rate limiting.
- **Milestones:**
  1. TS port and parity tests.
  2. Checker UI.
  3. Corpus browser.
  4. Generation samples.
  5. Deploy, which needs approval.

## 3. Paper outline

**Working title:** *Yaappu: Exact Venpa Meter Checking and Meter-Constrained Generation for Classical Tamil*

1. **Introduction.** Tamil prosody (ezhuthu→asai→seer→thalai→adi) is strict, but LLMs produce meter-violating venpa. Contributions: (i) an open checker with 96.5%, rising to ≥98%, on all 1,330 Thirukkural couplets; (ii) a re-segmentation search with a measured false-accept rate; (iii) a phonotactic filter; (iv) constrained decoding results (from EVAL.md).
2. **Background:** Tamil yappu rules, the venpa (kural) form, and why seer ≠ word (puṇarchi, kutriyalukaram, alabedai).
3. **Related work**
   - Computational Tamil prosody:
     - Raman et al., "Context Free Grammar for Natural Language constructs – An implementation for Venpa class of Tamil Poetry", Tamil Internet 2003 (INFITT), https://www.infitt.org/ti2003/papers/19_raman.pdf
     - CFG-based Tamil poem (paa) classification, IJIET, https://ijiet.org/papers/99-T038.pdf (author names still to be confirmed from the PDF)
     - Subasree Venkatasubramanian et al., CFG-based classification of Tamil poems into subclasses, CS & IT (AIRCC), https://airccj.org/CSCP/vol3/csit3617.pdf (title and venue still to be confirmed)
     - Tools: Avalokitam (V. Vinodh Rajan), https://github.com/virtualvinodh/avalokitam; Tamil_Prosody_Analyzer, https://github.com/naturalstupid/Tamil_Prosody_Analyzer
   - Meter-aware and constrained poetry generation:
     - Ormazabal et al., "PoeLM: A Meter- and Rhyme-Controllable Language Model for Unsupervised Poetry Generation", Findings of EMNLP 2022, https://aclanthology.org/2022.findings-emnlp.268
     - (authors to be confirmed from arXiv), "From Plain Text to Poetic Form: Generating Metrically-Constrained Sanskrit Verses", arXiv:2506.00815
     - Agarwal et al., "The Mechanical Bard: An Interpretable Machine Learning Approach to Shakespearean Sonnet Generation", ACL 2023 (short), https://aclanthology.org/2023.acl-short.140
     - Ghazvininejad et al., "Generating Topical Poetry" (Hafez), EMNLP 2016
   - Constrained decoding in general:
     - Hokamp & Liu, "Lexically Constrained Decoding for Sequence Generation Using Grid Beam Search", ACL 2017
     - Lu et al., "NeuroLogic Decoding", NAACL 2021
     - Willard & Louf, "Efficient Guided Generation for Large Language Models", arXiv:2307.09702 (2023)
   - *Before submission, every entry must be checked against its DOI or ACL Anthology page. The last four were not fetched in this session. Fill in author lists that are marked "to be confirmed"; do not guess them.*
4. **Method:** grapheme parsing, asai automaton, seer naming, the venthalai XOR rule, the final-seer rule; the re-segmentation search as cost-ordered search over licensed boundary shifts; the phonotactic filter.
5. **Evaluation:**
   - (a) Checker accuracy on raw and corrected Thirukkural, plus the error taxonomy (§1.1).
   - (b) False-accept rate on negative sets.
   - (c) Phonotactic false-rejection rate: 1.68% strict, 0.19% with junctions allowed.
   - (d) Generation: meter validity and fluency, baseline vs constrained (EVAL.md), with a human study by Tamil scholars.
6. **Error analysis:** source typos, editorial seer splits, the cases that stay ambiguous.
7. **Limitations and ethics:** only kural venpa is covered, the dependence on one edition, and the cultural sensitivity of generating "Thirukkural-like" text.
8. **Release:** code, the errata, and the demo URL.
