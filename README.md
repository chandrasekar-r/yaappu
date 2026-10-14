# yaappu — classical Tamil meter & phonotactics (Step 1 + 2)

Rule-based checker for **Kural Venba** meter and **Mozhimarapu** phonotactics, designed to be
compiled later into a constrained-decoding automaton for LLMs.

```python
from yaappu import check_kural, check_word, asai_split
check_kural("அகர முதல எழுத்தெல்லாம் ஆதி பகவன் முதற்றே உலகு.")
# Result(ok=True, seers=['புளிமா','புளிமா','புளிமாங்காய்','தேமா','புளிமா','புளிமா','பிறப்பு'])
check_word("பார்த்தான்")  # (True, 'ok')
```

## Rules implemented
- **Graphemes** (`graphemes.py`): uyir, mei, uyirmei, aytham.
- **Asai** (`asai.py`): ner = one syllable (+closing consonants); nirai = short syllable + next syllable (+consonants).
- **Seer**: 2-asai iyarseer (மா/விளம்), 3-asai venseer (காய்); கனி seers rejected.
- **Venthalai (XOR)**: after a 2-asai seer the next seer starts with the opposite of its last asai; after a காய் seer the next starts with ner.
- **Final seer**: நாள் / மலர் / காசு / பிறப்பு (1 asai, or 1 asai + final உ syllable).
- **Alabedai**: only a bare vowel letter written after the *matching* long vowel (ஆஅ, ஈஇ, ஊஉ, ஏஎ, ஐஇ, ஓஒ, ஔஉ); scanned both counted and uncounted.
- **Aytham** may be counted as a short unit (both readings tried).
- **Kutriyalukaram**: word-final short உ on a hard stop (not in a short-1-syllable word like அது) loses its உ before a vowel, between words and inside tokens written without sandhi.
- **Puṇarchi resyllabification**: a final consonant can join the next word's initial vowel (துன்பம் அஃது → துன்பமஃ | து).
- **Seer re-segmentation**: an 8-token couplet may join one adjacent pair into one seer.
- **Mozhimarapu** (`phonotactics.py`): legal initials (vowels, க ச த ந ப ம வ ய ஞ), legal final consonants (ஞ ண ந ம ன ய ர ல வ ழ ள), a consonant-cluster table (vallinam geminate only; ட்/ற் + க ச ப; nasal + homorganic stop; ய்/ர்/ழ் + stop/nasal; no ர்ர், ழ்ழ்), and 3-consonant clusters only as ய்/ர்/ழ் + geminate or nasal+stop (பார்த்தான், வாழ்க்கை, காய்ந்த). `check_text` re-joins seer-split fragments and allows word-final stops created by boundary gemination. `junctions=True` also accepts compounds written without sandhi (வான்நின்று).

## Data
`data/thirukkural.json` from [tk120404/thirukkural](https://github.com/tk120404/thirukkural) (word-separated edition; all 1,330 are Kural Venba).

## Benchmark
`python3 scripts/bench.py` → see [BENCHMARK.md](BENCHMARK.md).
