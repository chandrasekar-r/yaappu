const VIRAMA = "\u0BCD", AYTHAM = "\u0B83";
const VOWELS = { "\u0B85": "a", "\u0B86": "aa", "\u0B87": "i", "\u0B88": "ii", "\u0B89": "u", "\u0B8A": "uu", "\u0B8E": "e", "\u0B8F": "ee", "\u0B90": "ai", "\u0B92": "o", "\u0B93": "oo", "\u0B94": "au" };
const SIGNS = { "\u0BBE": "aa", "\u0BBF": "i", "\u0BC0": "ii", "\u0BC1": "u", "\u0BC2": "uu", "\u0BC6": "e", "\u0BC7": "ee", "\u0BC8": "ai", "\u0BCA": "o", "\u0BCB": "oo", "\u0BCC": "au" };
const SIGN_OF = Object.fromEntries(Object.entries(SIGNS).map(([k, v]) => [v, k]));
const CONSONANTS = new Set("\u0B95\u0B99\u0B9A\u0B9E\u0B9F\u0BA3\u0BA4\u0BA8\u0BAA\u0BAE\u0BAF\u0BB0\u0BB2\u0BB5\u0BB4\u0BB3\u0BB1\u0BA9"), GRANTHA = new Set("\u0B9C\u0BB7\u0BB8\u0BB9");
const SHORT = /* @__PURE__ */ new Set(["a", "i", "u", "e", "o"]), VALLINAM = new Set("\u0B95\u0B9A\u0B9F\u0BA4\u0BAA\u0BB1");
const NER = "ner", NIRAI = "nirai";
const ALABEDAI = { aa: "\u0B85", ii: "\u0B87", uu: "\u0B89", ee: "\u0B8E", ai: "\u0B87", oo: "\u0B92", au: "\u0B89" };
const isMei = (g) => g.vowel === null;
const isShort = (g) => g.vowel !== null && SHORT.has(g.vowel);
function parse(word) {
  const out = [];
  let i = 0;
  const n = word.length;
  while (i < n) {
    const ch = word[i];
    if (ch in VOWELS) {
      out.push({ text: ch, cons: null, vowel: VOWELS[ch] });
      i += 1;
    } else if (ch === AYTHAM) {
      out.push({ text: ch, cons: AYTHAM, vowel: null });
      i += 1;
    } else if (CONSONANTS.has(ch) || GRANTHA.has(ch)) {
      const nxt = i + 1 < n ? word[i + 1] : "";
      if (nxt === VIRAMA) {
        out.push({ text: ch + nxt, cons: ch, vowel: null });
        i += 2;
      } else if (nxt !== "" && nxt in SIGNS) {
        out.push({ text: ch + nxt, cons: ch, vowel: SIGNS[nxt] });
        i += 2;
      } else {
        out.push({ text: ch, cons: ch, vowel: "a" });
        i += 1;
      }
    } else i += 1;
  }
  return out;
}
const isAlabedai = (prev, g) => g.cons === null && g.vowel !== null && ALABEDAI[prev.vowel] === g.text;
class ScanError extends Error {
}
function asaiSplit(word, alabedaiCounts = true, aythamCounts = false) {
  let gs = parse(word);
  if (!gs.length) throw new ScanError("empty");
  if (!alabedaiCounts) gs = gs.filter((g, k) => !(k && isAlabedai(gs[k - 1], g)));
  if (aythamCounts) gs = gs.map((g) => g.cons === AYTHAM ? { text: g.text, cons: null, vowel: "a" } : g);
  const out = [];
  let i = 0;
  const n = gs.length;
  while (i < n) {
    const g = gs[i];
    if (isMei(g)) {
      if (!out.length) throw new ScanError("leading consonant");
      out[out.length - 1] = [out[out.length - 1][0], out[out.length - 1][1] + g.text];
      i += 1;
      continue;
    }
    let j, kind;
    if (isShort(g) && i + 1 < n && !isMei(gs[i + 1])) {
      j = i + 2;
      kind = NIRAI;
    } else {
      j = i + 1;
      kind = NER;
    }
    while (j < n && isMei(gs[j])) j += 1;
    out.push([kind, gs.slice(i, j).map((x) => x.text).join("")]);
    i = j;
  }
  return out;
}
function endsKutriyalukaram(word) {
  const gs = parse(word);
  if (gs.length < 2 || gs[gs.length - 1].vowel !== "u" || !VALLINAM.has(gs[gs.length - 1].cons)) return false;
  return !(gs.length === 2 && isShort(gs[0]));
}
const SEER_NAMES = {
  "ner,ner": "\u0BA4\u0BC7\u0BAE\u0BBE",
  "nirai,ner": "\u0BAA\u0BC1\u0BB3\u0BBF\u0BAE\u0BBE",
  "nirai,nirai": "\u0B95\u0BB0\u0BC1\u0BB5\u0BBF\u0BB3\u0BAE\u0BCD",
  "ner,nirai": "\u0B95\u0BC2\u0BB5\u0BBF\u0BB3\u0BAE\u0BCD",
  "ner,ner,ner": "\u0BA4\u0BC7\u0BAE\u0BBE\u0B99\u0BCD\u0B95\u0BBE\u0BAF\u0BCD",
  "nirai,ner,ner": "\u0BAA\u0BC1\u0BB3\u0BBF\u0BAE\u0BBE\u0B99\u0BCD\u0B95\u0BBE\u0BAF\u0BCD",
  "nirai,nirai,ner": "\u0B95\u0BB0\u0BC1\u0BB5\u0BBF\u0BB3\u0B99\u0BCD\u0B95\u0BBE\u0BAF\u0BCD",
  "ner,nirai,ner": "\u0B95\u0BC2\u0BB5\u0BBF\u0BB3\u0B99\u0BCD\u0B95\u0BBE\u0BAF\u0BCD",
  "ner,ner,nirai": "\u0BA4\u0BC7\u0BAE\u0BBE\u0B99\u0BCD\u0B95\u0BA9\u0BBF",
  "nirai,ner,nirai": "\u0BAA\u0BC1\u0BB3\u0BBF\u0BAE\u0BBE\u0B99\u0BCD\u0B95\u0BA9\u0BBF",
  "nirai,nirai,nirai": "\u0B95\u0BB0\u0BC1\u0BB5\u0BBF\u0BB3\u0B99\u0BCD\u0B95\u0BA9\u0BBF",
  "ner,nirai,nirai": "\u0B95\u0BC2\u0BB5\u0BBF\u0BB3\u0B99\u0BCD\u0B95\u0BA9\u0BBF"
};
const FINAL_NAMES = { "ner": "\u0BA8\u0BBE\u0BB3\u0BCD", "nirai": "\u0BAE\u0BB2\u0BB0\u0BCD", "ner,bu": "\u0B95\u0BBE\u0B9A\u0BC1", "nirai,bu": "\u0BAA\u0BBF\u0BB1\u0BAA\u0BCD\u0BAA\u0BC1" };
const R = (ok, error = null, seers = [], detail = "") => ({ ok, error, seers, detail });
const INNER = /([கசடதபற])\u0BC1(?=[அஆஇஈஉஊஎஏஐஒஓஔ])/g;
function elide(words) {
  const inner = (w) => w.replace(INNER, (m, c, off) => c + (!endsKutriyalukaram(w.slice(0, off + m.length)) ? "\u0BC1" : VIRAMA));
  const out = words.map(inner);
  for (let k = 0; k < out.length - 1; k++) {
    const nxt = parse(out[k + 1]);
    if (endsKutriyalukaram(out[k]) && nxt.length && nxt[0].cons === null && nxt[0].vowel) out[k] = out[k].slice(0, -1) + VIRAMA;
  }
  return out;
}
function resyllabify(w1, w2) {
  const a = parse(w1), b = parse(w2);
  if (!a.length || !b.length || !isMei(a[a.length - 1]) || a[a.length - 1].cons === AYTHAM || b[0].cons !== null) return null;
  let j = 1;
  while (j < b.length && isMei(b[j])) j += 1;
  if (j >= b.length) return null;
  const joined = a[a.length - 1].cons + (SIGN_OF[b[0].vowel] ?? "");
  return [a.slice(0, -1).map((g) => g.text).join("") + joined + b.slice(1, j).map((g) => g.text).join(""), b.slice(j).map((g) => g.text).join("")];
}
function variants(words) {
  let out = [words.slice()];
  for (let k = 0; k < words.length - 1; k++) {
    const nw = [];
    for (const v of out) {
      const r = resyllabify(v[k], v[k + 1]);
      if (r) nw.push([...v.slice(0, k), ...r, ...v.slice(k + 2)]);
    }
    out = out.concat(nw);
  }
  return out;
}
function readings(word) {
  const gs = parse(word);
  const hasAlb = gs.some((g, k) => k > 0 && isAlabedai(gs[k - 1], g));
  const alb = hasAlb ? [true, false] : [true];
  const ayt = word.includes(AYTHAM) ? [false, true] : [false];
  const res = [];
  for (const a of alb) for (const t of ayt) res.push(asaiSplit(word, a, t).map((x) => x[0]));
  return res;
}
const nextStartRequired = (p) => p.length === 2 ? p[1] === NER ? NIRAI : NER : NER;
function finalPattern(word, pat) {
  if (pat.length === 1) return pat.slice();
  if (pat.length === 2 && pat[1] === NER) {
    const g = parse(word);
    const l = g[g.length - 1];
    if (l.vowel === "u" && l.cons) return [pat[0], "bu"];
  }
  return null;
}
const pyRepr = (p) => "[" + p.map((x) => `'${x}'`).join(", ") + "]";
function* product(opts) {
  const idx = opts.map(() => 0);
  if (opts.some((o) => !o.length)) return;
  while (true) {
    yield idx.map((i, k2) => opts[k2][i]);
    let k = opts.length - 1;
    while (k >= 0) {
      idx[k]++;
      if (idx[k] < opts[k].length) break;
      idx[k] = 0;
      k--;
    }
    if (k < 0) return;
  }
}
function checkCombo(words, pats) {
  const names = [];
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
  const r = R(true, null, names);
  r.asai = pats;
  r.words = words;
  return r;
}
function checkKural(text) {
  let words = text.replace(/\n/g, " ").split(/\s+/).filter((w) => w && parse(w).length);
  if (words.length === 8) {
    const results = [];
    for (let k = 0; k < 7; k++) {
      const t = [...words.slice(0, k), elide(words.slice(k, k + 2))[0] + words[k + 1], ...words.slice(k + 2)];
      results.push(checkKural(t.join(" ")));
    }
    const good = results.filter((r) => r.ok);
    if (good.length) {
      good[0].detail = "joined two words into one seer";
      return good[0];
    }
    return R(false, "word_count", [], "8 words, no join scans");
  }
  if (words.length !== 7) return R(false, "word_count", [], String(words.length));
  words = elide(words);
  try {
    words.forEach(readings);
  } catch (e) {
    if (e instanceof ScanError) return R(false, "unscannable", [], e.message);
    throw e;
  }
  let best = null;
  const vs = variants(words);
  for (let k = 0; k < vs.length; k++) {
    const ws = vs[k];
    let options;
    try {
      options = ws.map(readings);
    } catch (e) {
      if (e instanceof ScanError) continue;
      throw e;
    }
    for (const combo of product(options)) {
      const r = checkCombo(ws, combo);
      if (r.ok) {
        if (k) r.detail = "boundary resyllabification";
        return r;
      }
      best = best || r;
    }
  }
  return best;
}
export {
  AYTHAM,
  NER,
  NIRAI,
  VIRAMA,
  asaiSplit,
  checkKural,
  endsKutriyalukaram,
  parse
};
