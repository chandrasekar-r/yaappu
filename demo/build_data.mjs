import { checkKural } from "./build/checker.mjs";
import fs from "fs";
const K = JSON.parse(fs.readFileSync("../data/thirukkural.json")).kural;
fs.writeFileSync("build/corpus.json", JSON.stringify(K.map(k => { const r = checkKural(k.Line1 + "\n" + k.Line2); return { n: k.Number, l1: k.Line1, l2: k.Line2, ok: r.ok, error: r.error, detail: r.detail, seers: r.seers }; })));
if (!fs.existsSync("build/gallery.json")) fs.writeFileSync("build/gallery.json", JSON.stringify({ note: "pending", rows: [] }));
console.log("corpus ok", K.length);
