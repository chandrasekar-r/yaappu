| model | mode | n | meter pass (check_kural) | pass (licensed checker) | 4+3 layout | distinct words / total | corpus-only vocab | copied ≥4 words of one kural | time/couplet s (mean / median) |
|---|---|---|---|---|---|---|---|---|---|
| Qwen/Qwen2.5-1.5B-Instruct | baseline | 20 | 0/20 (0%) | 0/20 (0%) | 2/20 | 146/157 | 0/20 (0%) | 0/20 | 8.9 / 8.1 |
| Qwen/Qwen2.5-1.5B-Instruct | constrained | 20 | 20/20 (100%) | 20/20 (100%) | 20/20 | 133/140 | 20/20 (100%) | 0/20 | 7.4 / 7.0 |
| unsloth/gemma-2-2b-it | baseline | 60 | 0/60 (0%) | 0/60 (0%) | 11/60 | 304/357 | 0/60 (0%) | 0/60 | 4.8 / 4.5 |
| unsloth/gemma-2-2b-it | constrained | 60 | 60/60 (100%) | 60/60 (100%) | 60/60 | 290/420 | 60/60 (100%) | 0/60 | 5.0 / 4.7 |
