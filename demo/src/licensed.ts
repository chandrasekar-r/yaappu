// Exact port of yaappu/reseg.py (check_kural_licensed, default licence L1) and yaappu/errata.normalize.
import { checkKural, parse, endsKutriyalukaram, VIRAMA, Result } from "./checker";
const PUNCT = /[^\u0B80-\u0BFF]/g, I_SIGN = "\u0BBF";
type Edit = [string, number, string];

function l1Sites(words: string[]): Edit[] {
  const sites: Edit[] = [];
  for (let k = 0; k < words.length - 1; k++) {
    const a = words[k].replace(PUNCT, ""), b = words[k + 1];
    if (endsKutriyalukaram(a) && b.startsWith("ய")) sites.push(["L1", k, "u"]);
    const gb = parse(b), pa = parse(a);
    if (gb.length > 1 && gb[0].cons && gb[0].vowel === "i" && gb[0].text.endsWith(I_SIGN)
      && gb[1].text.startsWith("ய") && pa.length && pa[pa.length - 1].vowel !== null) sites.push(["L1", k, "shift"]);
  }
  return sites;
}

function apply(words: string[], edits: Edit[]): string[] {
  const ws = words.slice();
  for (const [, k, x] of edits) {
    if (x === "u") { const a = ws[k].replace(PUNCT, ""); ws[k] = a.slice(0, -1) + VIRAMA; }
    else { const g0 = parse(ws[k + 1])[0].text; ws[k] = ws[k].replace(PUNCT, "") + g0.slice(0, -1) + VIRAMA; ws[k + 1] = ws[k + 1].slice(g0.length); }
  }
  return ws;
}

function combinations<T>(a: T[], n: number): T[][] {
  const out: T[][] = [];
  const rec = (start: number, cur: T[]) => {
    if (cur.length === n) { out.push(cur.slice()); return; }
    for (let i = start; i < a.length; i++) { cur.push(a[i]); rec(i + 1, cur); cur.pop(); }
  };
  rec(0, []); return out;
}

export function checkKuralLicensed(text: string): Result & { licensed_words?: string[] } {
  const r = checkKural(text);
  if (r.ok) return r;
  const words = text.replace(/\n/g, " ").split(/\s+/).filter(Boolean);
  const l1 = l1Sites(words);
  const cands: Edit[][] = [];
  for (let n = 1; n <= l1.length; n++) cands.push(...combinations(l1, n));
  for (const edits of cands) {
    const rr = checkKural(apply(words, edits).join(" "));
    if (rr.ok) { rr.detail = "licensed: " + edits.map(([a, k]) => `${a}@w${k + 1}`).join(","); return rr; }
  }
  return r;
}

export const normalize = (t: string) => t.replace(/\u0BC6\u0BB3(?![\u0BBE-\u0BCD\u0BD7])/g, "\u0BCC");
