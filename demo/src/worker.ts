import { checkKural, readings, elide, nextStartRequired, finalPattern, SEER_NAMES, FINAL_NAMES, parse, Result } from "./checker";
import { checkKuralLicensed, normalize } from "./licensed";
import corpus from "../build/corpus.json";
import gallery from "../build/gallery.json";
import { CSS, JS } from "./ui";

const EXPLAIN: Record<string, string> = {
  word_count: "A kural venba has exactly 7 seers: 4 on the first line and 3 on the second.",
  unscannable: "A word starts with a pure consonant (mei), so it can't be divided into asai.",
  seer_length: "Every seer except the last must have 2 or 3 asai.",
  kani_seer: "A kani seer (3 asai ending in nirai) is not allowed in a venpa.",
  final_seer: "The last seer must be நாள் (ner), மலர் (nirai), காசு (ner+bu) or பிறப்பு (nirai+bu).",
  thalai: "Venthalai linkage broke: after a மா seer the next must start with nirai; after a விளம் or காய் seer it must start with ner.",
};

function analyze(text: string, r: Result) {
  let words: string[] = r.words || [], asai: (string[] | null)[] = r.asai || [];
  if (!r.ok) {
    const toks = text.replace(/\n/g, " ").split(/\s+/).filter(w => w && parse(w).length);
    words = toks.length === 7 ? elide(toks) : toks;
    asai = words.map(w => { try { return readings(w)[0]; } catch { return null; } });
  }
  const seers = words.map((w, i) => {
    const p = asai[i]; if (!p) return { word: w, asai: null, name: null };
    if (i === 6 && words.length === 7) { const f = finalPattern(w, p); return { word: w, asai: p, name: f ? FINAL_NAMES[f.join(",")] : null }; }
    return { word: w, asai: p, name: SEER_NAMES[p.join(",")] || null };
  });
  const links = seers.slice(0, -1).map((s, i) => {
    const nx = seers[i + 1];
    if (!s.asai || !nx.asai || s.asai.length < 2 || s.asai.length > 3) return null;
    return nextStartRequired(s.asai) === nx.asai[0];
  });
  return { seers, links, explain: r.error ? EXPLAIN[r.error] || "" : "" };
}

function check(text: string, mode: string) {
  const r = mode === "base" ? checkKural(text) : checkKuralLicensed(text);
  return { ...r, mode: mode === "base" ? "base" : "licensed", analysis: analyze(text, r) };
}

const esc = (s: unknown) => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c] as string));
const C = corpus as any[];
const PASS = C.filter(k => k.ok).length;

function shell(page: string, title: string, body: string) {
  const nav = [["/", "Checker"], ["/corpus", "Corpus"], ["/gallery", "Gallery"], ["/about", "About"]]
    .map(([h, t]) => `<a href="${h}"${h === page ? ' aria-current="page"' : ""}>${t}</a>`).join("");
  return new Response(`<!doctype html><html lang="ta"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)} · யாப்பு yaappu</title>
<meta name="description" content="yaappu checks Tamil kural venba meter: asai, seer and venthalai, in the browser.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Mukta+Malar:wght@400;600;700&family=Noto+Serif+Tamil:wght@500;700&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>${CSS}</style><script>document.documentElement.dataset.theme=localStorage.theme||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light')</script></head>
<body data-page="${page}"><header class="top"><a class="brand" href="/"><span class="ta">யாப்பு</span> yaappu</a><nav>${nav}</nav>
<button id="theme" class="icon" aria-label="Toggle dark mode">◐</button></header><main>${body}</main>
<footer>yaappu · Tamil prosody toolkit · <a href="/api/corpus">API</a></footer><script>${JS}</script></body></html>`,
    { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=300" } });
}

const pages: Record<string, () => Response> = {
  "/": () => shell("/", "Kural checker", `<section class="hero"><h1>Check the meter of any <span class="ta">குறள் வெண்பா</span></h1>
<p class="lead">yaappu splits a couplet into asai and seer, then checks every venthalai link, the way a Tamil prosodist would.</p>
<p class="stat"><b>${(100 * PASS / C.length).toFixed(2)}%</b> of the 1,330 Thirukkural couplets pass (source corrections applied)</p></section>
<section class="card checker"><label for="kt" class="lbl">Paste a kural (two lines, 4 + 3 seers)</label>
<textarea id="kt" rows="3" lang="ta" class="ta" placeholder="அகர முதல எழுத்தெல்லாம் ஆதி&#10;பகவன் முதற்றே உலகு."></textarea>
<div class="row"><button id="go" class="primary">Check meter</button><button class="ex" data-ex="0">Example: valid</button><button class="ex" data-ex="1">Example: broken</button><button class="ex" data-ex="2">Example: re-segmented</button>
<label class="tog"><input type="checkbox" id="lic" checked> licensed re-segmentation</label></div>
<div id="out" aria-live="polite"></div></section>
<section class="legend"><span class="chip ner">ner</span> one syllable · <span class="chip nirai">nirai</span> short + one more syllable · <span class="lk ok">✓</span> venthalai link holds · <span class="lk bad">✗</span> broken link</section>`),
  "/corpus": () => shell("/corpus", "Corpus", `<section class="hero sm"><h1>Thirukkural corpus</h1><p class="lead">${PASS}/${C.length} pass. Search by word or number, and filter by result.</p></section>
<div class="tools card"><input id="q" type="search" placeholder="Search: அறம், 1143, கெளவை…" lang="ta" class="ta"><div class="seg" id="flt"><button data-f="all" class="on">All</button><button data-f="pass">Pass</button><button data-f="fail">Fail (${C.length - PASS})</button><button data-f="fixed">Corrected</button></div></div>
<p id="count" class="muted"></p><div id="grid" class="grid"></div><nav id="pager" class="pager"></nav>`),
  "/gallery": () => {
    const g = gallery as any;
    const card = (t: string, ok: boolean, kind: string) => `<div class="gcol ${kind}"><div class="ghead">${kind === "b" ? "Baseline" : "Constrained"}<span class="badge ${ok ? "ok" : "bad"}">${ok ? "✓ meter" : "✗ meter"}</span></div><p class="kural ta">${esc(t || "(empty)").replace(/\n/g, "<br>")}</p></div>`;
    return shell("/gallery", "Gallery", `<section class="hero sm"><h1>Baseline vs constrained</h1><p class="lead">The same model (gemma-2-2b-it) and the same prompt for both columns. The constrained decoder guarantees the meter. It does not guarantee the meaning.</p></section>
<div class="glist">${g.rows.map((r: any) => `<article class="card gcard"><h3 class="ta">${esc(r.topic)}</h3><div class="gpair">${card(r.baseline, r.baseline_ok, "b")}${card(r.constrained, r.constrained_ok, "c")}</div></article>`).join("")}</div>
<p class="muted small">${esc(g.note)}</p>`);
  },
  "/about": () => shell("/about", "About", `<section class="hero sm"><h1>About yaappu</h1></section><article class="card prose">
<p><b>yaappu</b> (<span class="ta">யாப்பு</span>, "prosody") is a rule-based Tamil meter toolkit. It includes a kural venba checker, a phonotactic filter and a constrained decoder that makes a language model write couplets that always scan.</p>
<h3>How the checker works</h3><ol><li>The text is split into letters: kuril (short), nedil (long) and ottru (pure consonant).</li><li>Letters are grouped into asai. <span class="chip ner">ner</span> is one syllable plus its consonants; <span class="chip nirai">nirai</span> is a short syllable plus the next syllable.</li><li>Asai are grouped into seer: தேமா, புளிமா, கூவிளம், கருவிளம் and the காய் seers. Kani seers are not allowed.</li><li>Venthalai: a மா seer must be followed by nirai; a விளம் or காய் seer by ner. The last seer must be நாள், மலர், காசு or பிறப்பு.</li><li>Kutriyalukaram elision and resyllabification across word boundaries are handled. The <i>licensed</i> mode also applies kutriyalikaram, for example செல்வத்திற்கு யாதெனின்.</li></ol>
<h3>Numbers</h3><p>${PASS}/1330 kurals pass with the licensed checker on source-corrected text. 13 typo fixes were verified against Tamil Wikisource, plus a ௌ normalisation. The base checker passes 1284/1330 on the raw text. This site's TypeScript checker gives the same result as the Python reference on 6,650 test cases.</p>
<h3>API</h3><pre>POST /api/check {"text": "...", "mode": "licensed" | "base"}
GET  /api/corpus</pre></article>`),
};

export default {
  async fetch(req: Request): Promise<Response> {
    const u = new URL(req.url);
    if (u.pathname === "/api/check" && req.method === "POST") {
      let body: any;
      try { body = await req.json(); } catch { return Response.json({ error: "expected JSON {text}" }, { status: 400 }); }
      const text = String(body?.text ?? "");
      if (text.length > 2000) return Response.json({ error: "text too long" }, { status: 413 });
      return Response.json(check(text, String(body?.mode || u.searchParams.get("mode") || "licensed")));
    }
    if (u.pathname === "/" && req.method === "POST") {   // no-JS form fallback
      const t = String((await req.formData()).get("text") ?? "").slice(0, 2000);
      return Response.redirect(new URL("/#" + encodeURIComponent(t), req.url).toString(), 303);
    }
    if (u.pathname === "/api/corpus") return Response.json(C, { headers: { "cache-control": "public, max-age=3600" } });
    if (u.pathname === "/api/gallery") return Response.json(gallery);
    const p = pages[u.pathname.replace(/\/$/, "") || "/"];
    if (p) return p(); const nf = shell("", "Not found", `<section class="hero sm"><h1>404</h1><p class="lead">That page doesn't exist. <a href="/">Back to the checker</a>.</p></section>`); return new Response(nf.body, { status: 404, headers: nf.headers });
  },
};
