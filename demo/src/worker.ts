import { checkKural, Result } from "./checker";
import corpus from "../build/corpus.json";
import gallery from "../build/gallery.json";

type K = { n: number; l1: string; l2: string; ok: boolean; error: string | null; detail: string; seers: string[] };
const C = corpus as K[];
const esc = (s: string) => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c] as string));

const page = (title: string, body: string) => new Response(`<!doctype html><html lang="ta"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)} · yaappu</title>
<style>body{font-family:system-ui,"Noto Sans Tamil",sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem;line-height:1.6;color:#222}
nav a{margin-right:1rem}textarea{width:100%;font-size:1.1rem}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #ddd;padding:.3rem;text-align:left;vertical-align:top}
.ok{color:#0a7a2f;font-weight:600}.bad{color:#b00020;font-weight:600}.k{white-space:pre-line;font-size:1.05rem}small{color:#666}button{font-size:1rem;padding:.3rem 1rem}</style></head>
<body><nav><b>yaappu</b> · <a href="/">Checker</a><a href="/corpus">Corpus</a><a href="/gallery">Gallery</a><a href="/about">About</a></nav>${body}</body></html>`,
  { headers: { "content-type": "text/html; charset=utf-8" } });

function resultHtml(r: Result) {
  const rows = (r.words || []).map((w, i) => `<tr><td>${i + 1}</td><td>${esc(w)}</td><td>${esc((r.asai || [])[i]?.join(" + "))}</td><td>${esc(r.seers[i])}</td></tr>`).join("");
  return `<p class="${r.ok ? "ok" : "bad"}">${r.ok ? "✓ Valid kural venba" : "✗ Not a valid kural venba"}${r.error ? ` (${esc(r.error)})` : ""}</p>
  ${r.detail ? `<p><small>${esc(r.detail)}</small></p>` : ""}
  ${rows ? `<table><tr><th>#</th><th>seer</th><th>asai</th><th>vaaippaadu</th></tr>${rows}</table>` : r.seers.length ? `<p>seers so far: ${esc(r.seers.join(" · "))}</p>` : ""}`;
}

function checkerPage(text = "", r?: Result) {
  return page("Kural checker", `<h1>Kural venba meter checker</h1>
<p>Paste a two-line kural (4 + 3 seers). The checker splits it into asai and seer, checks the venthalai links and the final seer. It is a TypeScript port of the Python checker and gives the same result on all 1,330 Thirukkural couplets.</p>
<form method="post" action="/"><textarea name="text" rows="3" placeholder="அகர முதல எழுத்தெல்லாம் ஆதி&#10;பகவன் முதற்றே உலகு.">${esc(text)}</textarea><p><button>Check</button></p></form>
${r ? resultHtml(r) : ""}<p><small>API: <code>POST /api/check</code> with JSON <code>{"text": "..."}</code>.</small></p>`);
}

export default {
  async fetch(req: Request): Promise<Response> {
    const u = new URL(req.url);
    if (u.pathname === "/api/check" && req.method === "POST") {
      let text = "";
      try { text = String(((await req.json()) as any).text ?? ""); } catch { return Response.json({ error: "expected JSON {text}" }, { status: 400 }); }
      if (text.length > 2000) return Response.json({ error: "text too long" }, { status: 413 });
      return Response.json(checkKural(text));
    }
    if (u.pathname === "/" && req.method === "POST") {
      const f = await req.formData(); const t = String(f.get("text") ?? "").slice(0, 2000);
      return checkerPage(t, checkKural(t));
    }
    if (u.pathname === "/") return checkerPage();
    if (u.pathname === "/api/corpus") return Response.json(C);
    if (u.pathname === "/corpus") {
      const f = u.searchParams.get("filter") || "all";
      const rows = C.filter(k => f === "pass" ? k.ok : f === "fail" ? !k.ok : true);
      const pass = C.filter(k => k.ok).length;
      return page("Corpus", `<h1>Thirukkural corpus (raw source text)</h1>
<p>${pass}/${C.length} pass (${(100 * pass / C.length).toFixed(2)}%). Filter:
<a href="/corpus">all</a> · <a href="/corpus?filter=pass">pass</a> · <a href="/corpus?filter=fail">fail (${C.length - pass})</a>. Showing ${rows.length}.</p>
<table><tr><th>#</th><th>kural</th><th>result</th></tr>${rows.map(k => `<tr><td>${k.n}</td><td class="k">${esc(k.l1)}\n${esc(k.l2)}</td><td class="${k.ok ? "ok" : "bad"}">${k.ok ? "✓" : "✗ " + esc(k.error)}<br><small>${esc(k.ok ? k.seers.join(" · ") : k.detail)}</small></td></tr>`).join("")}</table>`);
    }
    if (u.pathname === "/gallery") {
      const g = gallery as any;
      return page("Gallery", `<h1>Generated couplets: baseline vs constrained</h1>
<p>${esc(g.note)}</p><table><tr><th>topic</th><th>baseline (unconstrained)</th><th>constrained + reranked</th></tr>
${g.rows.map((r: any) => `<tr><td>${esc(r.topic)}</td><td class="k">${esc(r.baseline)}<br><span class="${r.baseline_ok ? "ok" : "bad"}">${r.baseline_ok ? "✓" : "✗"} meter</span></td><td class="k">${esc(r.constrained)}<br><span class="${r.constrained_ok ? "ok" : "bad"}">${r.constrained_ok ? "✓" : "✗"} meter</span></td></tr>`).join("")}</table>`);
    }
    if (u.pathname === "/about") return page("About", `<h1>About</h1><p><b>yaappu</b> is a Tamil prosody (யாப்பு) toolkit with a kural venba meter checker, a phonotactic filter, and a word-level constrained decoder that makes a language model produce couplets that always scan. The constraint guarantees the meter, not the meaning.</p><p><small>The gallery couplets were generated offline with gemma-2-2b-it on CPU. Nothing on this site calls an LLM.</small></p>`);
    return new Response("not found", { status: 404 });
  },
};
