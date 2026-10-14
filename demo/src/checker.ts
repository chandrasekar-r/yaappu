// Exact TypeScript port of yaappu (graphemes.py, asai.py, venba.py: check_kural).
// Parity with Python is enforced by demo/parity.mjs on all 1,330 kurals.
export const VIRAMA = "\u0BCD", AYTHAM = "\u0B83";
const VOWELS: Record<string, string> = { "அ": "a", "ஆ": "aa", "இ": "i", "ஈ": "ii", "உ": "u", "ஊ": "uu", "எ": "e", "ஏ": "ee", "ஐ": "ai", "ஒ": "o", "ஓ": "oo", "ஔ": "au" };
const SIGNS: Record<string, string> = { "\u0BBE": "aa", "\u0BBF": "i", "\u0BC0": "ii", "\u0BC1": "u", "\u0BC2": "uu", "\u0BC6": "e", "\u0BC7": "ee", "\u0BC8": "ai", "\u0BCA": "o", "\u0BCB": "oo", "\u0BCC": "au" };
const SIGN_OF: Record<string, string> = Object.fromEntries(Object.entries(SIGNS).map(([k, v]) => [v, k]));
const CONSONANTS = new Set("கஙசஞடணதநபமயரலவழளறன"), GRANTHA = new Set("ஜஷஸஹ");
const SHORT = new Set(["a", "i", "u", "e", "o"]), VALLINAM = new Set("கசடதபற");
export const NER = "ner", NIRAI = "nirai";
const ALABEDAI: Record<string, string> = { aa: "அ", ii: "இ", uu: "உ", ee: "எ", ai: "இ", oo: "ஒ", au: "உ" };

export interface G { text: string; cons: string | null; vowel: string | null }
const isMei = (g: G) => g.vowel === null;
const isShort = (g: G) => g.vowel !== null && SHORT.has(g.vowel);

export function parse(word: string): G[] {
  const out: G[] = []; let i = 0; const n = word.length;
  while (i < n) {
    const ch = word[i];
    if (ch in VOWELS) { out.push({ text: ch, cons: null, vowel: VOWELS[ch] }); i += 1; }
    else if (ch === AYTHAM) { out.push({ text: ch, cons: AYTHAM, vowel: null }); i += 1; }
    else if (CONSONANTS.has(ch) || GRANTHA.has(ch)) {
      const nxt = i + 1 < n ? word[i + 1] : "";
      if (nxt === VIRAMA) { out.push({ text: ch + nxt, cons: ch, vowel: null }); i += 2; }
      else if (nxt !== "" && nxt in SIGNS) { out.push({ text: ch + nxt, cons: ch, vowel: SIGNS[nxt] }); i += 2; }
      else { out.push({ text: ch, cons: ch, vowel: "a" }); i += 1; }
    } else i += 1;
  }
  return out;
}

const isAlabedai = (prev: G, g: G) => g.cons === null && g.vowel !== null && ALABEDAI[prev.vowel as string] === g.text;

class ScanError extends Error {}

export function asaiSplit(word: string, alabedaiCounts = true, aythamCounts = false): [string, string][] {
  let gs = parse(word);
  if (!gs.length) throw new ScanError("empty");
  if (!alabedaiCounts) gs = gs.filter((g, k) => !(k && isAlabedai(gs[k - 1], g)));
  if (aythamCounts) gs = gs.map(g => g.cons === AYTHAM ? { text: g.text, cons: null, vowel: "a" } : g);
  const out: [string, string][] = []; let i = 0; const n = gs.length;
  while (i < n) {
    const g = gs[i];
    if (isMei(g)) {
      if (!out.length) throw new ScanError("leading consonant");
      out[out.length - 1] = [out[out.length - 1][0], out[out.length - 1][1] + g.text]; i += 1; continue;
    }
    let j: number, kind: string;
    if (isShort(g) && i + 1 < n && !isMei(gs[i + 1])) { j = i + 2; kind = NIRAI; } else { j = i + 1; kind = NER; }
    while (j < n && isMei(gs[j])) j += 1;
    out.push([kind, gs.slice(i, j).map(x => x.text).join("")]); i = j;
  }
  return out;
}

export function endsKutriyalukaram(word: string): boolean {
  const gs = parse(word);
  if (gs.length < 2 || gs[gs.length - 1].vowel !== "u" || !VALLINAM.has(gs[gs.length - 1].cons as string)) return false;
  return !(gs.length === 2 && isShort(gs[0]));
}

export const SEER_NAMES: Record<string, string> = {
  "ner,ner": "தேமா", "nirai,ner": "புளிமா", "nirai,nirai": "கருவிளம்", "ner,nirai": "கூவிளம்",
  "ner,ner,ner": "தேமாங்காய்", "nirai,ner,ner": "புளிமாங்காய்", "nirai,nirai,ner": "கருவிளங்காய்", "ner,nirai,ner": "கூவிளங்காய்",
  "ner,ner,nirai": "தேமாங்கனி", "nirai,ner,nirai": "புளிமாங்கனி", "nirai,nirai,nirai": "கருவிளங்கனி", "ner,nirai,nirai": "கூவிளங்கனி",
};
export const FINAL_NAMES: Record<string, string> = { "ner": "நாள்", "nirai": "மலர்", "ner,bu": "காசு", "nirai,bu": "பிறப்பு" };

export interface Result { ok: boolean; error: string | null; seers: string[]; detail: string; asai?: string[][]; words?: string[] }
const R = (ok: boolean, error: string | null = null, seers: string[] = [], detail = ""): Result => ({ ok, error, seers, detail });

const INNER = /([கசடதபற])\u0BC1(?=[அஆஇஈஉஊஎஏஐஒஓஔ])/g;
export function elide(words: string[]): string[] {
  const inner = (w: string) => w.replace(INNER, (m: string, c: string, off: number) =>
    c + (!endsKutriyalukaram(w.slice(0, off + m.length)) ? "\u0BC1" : VIRAMA));
  const out = words.map(inner);
  for (let k = 0; k < out.length - 1; k++) {
    const nxt = parse(out[k + 1]);
    if (endsKutriyalukaram(out[k]) && nxt.length && nxt[0].cons === null && nxt[0].vowel) out[k] = out[k].slice(0, -1) + VIRAMA;
  }
  return out;
}

function resyllabify(w1: string, w2: string): [string, string] | null {
  const a = parse(w1), b = parse(w2);
  if (!a.length || !b.length || !isMei(a[a.length - 1]) || a[a.length - 1].cons === AYTHAM || b[0].cons !== null) return null;
  let j = 1;
  while (j < b.length && isMei(b[j])) j += 1;
  if (j >= b.length) return null;
  const joined = (a[a.length - 1].cons as string) + (SIGN_OF[b[0].vowel as string] ?? "");
  return [a.slice(0, -1).map(g => g.text).join("") + joined + b.slice(1, j).map(g => g.text).join(""), b.slice(j).map(g => g.text).join("")];
}

function variants(words: string[]): string[][] {
  let out = [words.slice()];
  for (let k = 0; k < words.length - 1; k++) {
    const nw: string[][] = [];
    for (const v of out) { const r = resyllabify(v[k], v[k + 1]); if (r) nw.push([...v.slice(0, k), ...r, ...v.slice(k + 2)]); }
    out = out.concat(nw);
  }
  return out;
}

export function readings(word: string): string[][] {
  const gs = parse(word);
  const hasAlb = gs.some((g, k) => k > 0 && isAlabedai(gs[k - 1], g));
  const alb = hasAlb ? [true, false] : [true];
  const ayt = word.includes(AYTHAM) ? [false, true] : [false];
  const res: string[][] = [];
  for (const a of alb) for (const t of ayt) res.push(asaiSplit(word, a, t).map(x => x[0]));
  return res;
}

export const nextStartRequired = (p: string[]) => p.length === 2 ? (p[1] === NER ? NIRAI : NER) : NER;

export function finalPattern(word: string, pat: string[]): string[] | null {
  if (pat.length === 1) return pat.slice();
  if (pat.length === 2 && pat[1] === NER) { const g = parse(word); const l = g[g.length - 1]; if (l.vowel === "u" && l.cons) return [pat[0], "bu"]; }
  return null;
}

const pyRepr = (p: string[]) => "[" + p.map(x => `'${x}'`).join(", ") + "]";

function* product(opts: string[][][]): Generator<string[][]> {
  const idx = opts.map(() => 0);
  if (opts.some(o => !o.length)) return;
  while (true) {
    yield idx.map((i, k) => opts[k][i]);
    let k = opts.length - 1;
    while (k >= 0) { idx[k]++; if (idx[k] < opts[k].length) break; idx[k] = 0; k--; }
    if (k < 0) return;
  }
}

function checkCombo(words: string[], pats: string[][]): Result {
  const names: string[] = [];
  for (let k = 0; k < 6; k++) {
    const w = words[k], p = pats[k];
    if (p.length !== 2 && p.length !== 3) return R(false, "seer_length", names, `seer${k + 1} ${w} ${p.length} asai`);
    if (p.length === 3 && p[2] === NIRAI) return R(false, "kani_seer", names, `seer${k + 1} ${w} ${SEER_NAMES[p.join(",")]}`);
    names.push(SEER_NAMES[p.join(",")]);
  }
  const fp = finalPattern(words[6], pats[6]);
  if (fp === null) return R(false, "final_seer", names, `${words[6]} ${pyRepr(pats[6])}`);
  names.push(FINAL_NAMES[fp.join(",")]);
  for (let k = 0; k < 6; k++) {
    const need = nextStartRequired(pats[k]), got = pats[k + 1][0];
    if (need !== got) return R(false, "thalai", names, `${words[k]}->${words[k + 1]} need ${need}`);
  }
  const r = R(true, null, names); r.asai = pats; r.words = words; return r;
}

export function checkKural(text: string): Result {
  let words = text.replace(/\n/g, " ").split(/\s+/).filter(w => w && parse(w).length);
  if (words.length === 8) {
    const results: Result[] = [];
    for (let k = 0; k < 7; k++) {
      const t = [...words.slice(0, k), elide(words.slice(k, k + 2))[0] + words[k + 1], ...words.slice(k + 2)];
      results.push(checkKural(t.join(" ")));
    }
    const good = results.filter(r => r.ok);
    if (good.length) { good[0].detail = "joined two words into one seer"; return good[0]; }
    return R(false, "word_count", [], "8 words, no join scans");
  }
  if (words.length !== 7) return R(false, "word_count", [], String(words.length));
  words = elide(words);
  try { words.forEach(readings); } catch (e) { if (e instanceof ScanError) return R(false, "unscannable", [], e.message); throw e; }
  let best: Result | null = null;
  const vs = variants(words);
  for (let k = 0; k < vs.length; k++) {
    const ws = vs[k]; let options: string[][][];
    try { options = ws.map(readings); } catch (e) { if (e instanceof ScanError) continue; throw e; }
    for (const combo of product(options)) {
      const r = checkCombo(ws, combo);
      if (r.ok) { if (k) r.detail = "boundary resyllabification"; return r; }
      best = best || r;
    }
  }
  return best as Result;
}
