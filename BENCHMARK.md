## Meter: 1284/1330 = 96.54% pass

- **thalai** (18): 4: வேண்டாமை->இலானடி need ner; 39: இன்பம்->மற்றெல்லாம் need nirai; 114: காணப்ப->படும். need ner; 170: இல்லை->அஃத்இல்லார் need nirai; 254: அருளல்ல->தியாதெனிற் need ner; 278: மாண்டார்->நீராடி need nirai; 360: மயக்கம்->இவ்மூன்றன் need nirai; 653: ஒஓதல்->வேண்டும் need nirai; 719: சொல்லு->வார். need nirai; 738: நாட்டிவ்->வைந்து. need nirai; 764: அழிவின்றி->அறைபோகா need ner; 775: வேல்கொண->டெறிய need ner; 778: செறினும்->சீர்குன்றல் need nirai; 844: எனப்படுவ->தியாதெனின் need ner; 882: வாள்போல->பகைவரை need ner; 1134: உய்க்கும்->நாணொடு need nirai; 1202: எனைத்தொனற்->இனிதேகாண் need ner; 1249: லவரால்->உள்ளிநீ need nirai
- **source typo (suspected)** (8): 154: வேண்டின்->பொற்யுடைமை need nirai; 599: leading consonant; 855: யாரே->மிக்லூக்கும் need nirai; 858: அதனை->மிக்லூக்கின் need nirai; 1143: ஊரறிந்த->கெளவை need ner; 1147: ஊரவர்->கெளவை need ner; 1148: என்றற்றால்->கெளவையால் need ner; 1150: யாம்வேண்டும்->கெளவை need ner
- **seer_length** (7): 93: seer2 அமர்ந்த் 1 asai; 178: seer2 செல்வத்திற்கு 4 asai; 287: seer6 புரிந்தார்கண்ட 4 asai; 585: seer3 கண்ணஞ்சாது 4 asai; 832: seer1 பேதைமையுள் 4 asai; 895: seer1 யாண்டுச்சென்று 4 asai; 1299: seer1 துன்பத்திற்கு 4 asai
- **kani_seer** (6): 98: seer1 சிறுமையுவு புளிமாங்கனி; 291: seer2 எனப்படுவது கருவிளங்கனி; 324: seer2 எனப்படுவது கருவிளங்கனி; 795: seer5 வல்லார்நடப் தேமாங்கனி; 801: seer2 எனப்படுவது கருவிளங்கனி; 1041: seer2 இன்னாதது தேமாங்கனி
- **word_count** (4): 42: 6; 689: 6; 976: 9; 1117: 8 words, no join scans
- **unscannable** (2): 434: leading consonant; 651: leading consonant
- **final_seer** (1): 269: டவர்க்குல். ['nirai', 'ner']

## Phonotactics (unsandhied-compound junctions strict): 154/9158 words rejected = 1.68%

- cluster ன்நோ (10): என்நோற்றான், பின்நோக்காச், அறன்நோக்கி, புறன்நோக்கிப்
- cluster ள்நீ (6): பொருள்நீங்கிப், அருள்நீங்கி, இருள்நீங்கி, மருள்நீங்கி
- cluster ல்நோ (6): அல்லல்நோய், உய்வில்நோய், பைதல்நோய், பைதல்நோய்
- cluster ல்ம (5): அல்லால்மற்றாங்கே, புதல்மறைந்து, நூல்மறப்பர், கடல்மன்னும்
- cluster ன்த (5): தம்மின்தம், மகன்தந்தைக்கு, இவன்தந்தை, ஒருவன்தன்
- cluster ன்து (5): தான்துவ்வான், தன்துணை, இன்துணையாக், தான்துவ்வான்
- cluster ன்நி (4): வான்நின்று, முன்நிற், முன்நின்று, முன்நின்று
- cluster ம்த (4): தம்தம், பொருளும்தன், வைக்கும்தன், யாம்தம்மை
- cluster ர்ந் (4): காய்கவர்ந், சொல்லாரிழைத்துணர்ந், நிலைதளர்ந், வறங்கூர்ந்
- cluster ன்தூ (4): பயன்தூக்கார், நயன்தூக்கின், பயன்தூக்கிப், நயன்தூக்கி

## Phonotactics (unsandhied-compound junctions allowed): 17/9158 words rejected = 0.19%

- cluster ர்ந் (4): காய்கவர்ந், சொல்லாரிழைத்துணர்ந், நிலைதளர்ந், வறங்கூர்ந்
- bad final க் (2): சூழ்வாரைக், தமராகிக்
- bad final ஃ (2): வெறுக்கைஅஃ, ஆணிஅஃ
- cluster க்லூ (2): மிக்லூக்கும், மிக்லூக்கின்
- cluster க்த (1): மனைக்தக்க
- cluster ற்யு (1): பொற்யுடைமை
- cluster ய்ந் (1): போர்த்துமேய்ந்
- cluster ந்த் (1): அற்றந்த்ரூஉம்
- cluster வ்ரு (1): யானை஦வ்ருஉம்
- cluster ம்த் (1): ஆக்கம்த்ருஉம்

## Errata + rule-licensed re-segmentation (scripts/bench_reseg.py)

Reproduce: `python3 scripts/bench_reseg.py` (about 5 s). Atom's baseline shuffle control: `python3 scripts/bench.py | grep Shuffle` gives 14/1305. That needs Atom's uncommitted bench.py edit; `bench_reseg.py` repeats the same procedure (seed 0, raw 7-word kurals) and gets the same 14/1305.

- `errata=typo`: ெ+ள→ௌ normalisation plus 13 typo fixes verified against Tamil Wikisource *திருக்குறள், மூலம்*, with Project Madurai readings recorded. `errata=all` also applies 5 editorial re-segmentations from the same source. Both live in `data/errata.json`; the raw data is never modified (`yaappu.errata.load_kurals`).
- L1 = kutriyalikaram license (yaappu/reseg.py, the default). L2 = aikaarakkurukkam (opt-in; not adopted, because it adds a false accept and recovers nothing on errata text).

| checker | raw | errata=typo | errata=all | shuffle false-accept |
|---|---|---|---|---|
| baseline | 1284/1330 = 96.54% | 1301/1330 = 97.82% | 1306/1330 = 98.20% | 14/1305 = 1.07% |
| L1 | 1294/1330 = 97.29% | 1311/1330 = 98.57% | 1316/1330 = 98.95% | 14/1305 = 1.07% |
| L1+L2 | 1295/1330 = 97.37% | 1311/1330 = 98.57% | 1316/1330 = 98.95% | 15/1305 = 1.15% |

Remaining failures (default L1, errata=all):
- **thalai** (12): 4: வேண்டாமை->இலானடி need ner; 114: காணப்ப->படும். need ner; 170: இல்லை->அஃத்இல்லார் need nirai; 278: மாண்டார்->நீராடி need nirai; 719: சொல்லு->வார். need nirai; 738: நாட்டிவ்->வைந்து. need nirai; 764: அழிவின்றி->அறைபோகா need ner; 778: செறினும்->சீர்குன்றல் need nirai; 858: அதனை->மிக்லூக்கின் need nirai; 882: வாள்போல->பகைவரை need ner; 1134: உய்க்கும்->நாணொடு need nirai; 1249: லவரால்->உள்ளிநீ need nirai
- **unscannable** (1): 434: leading consonant
- **seer_length** (1): 832: seer1 பேதைமையுள் 4 asai

Recovered by licenses (10): 178 (licensed: L1@w2); 254 (licensed: L1@w1); 291 (licensed: L1@w2); 324 (licensed: L1@w2); 585 (licensed: L1@w3); 801 (licensed: L1@w2); 844 (licensed: L1@w2); 895 (licensed: L1@w1); 1041 (licensed: L1@w2); 1299 (licensed: L1@w1)
