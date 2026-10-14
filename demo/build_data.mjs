import { checkKuralLicensed } from "./build/licensed.mjs";
import fs from "fs";
const K = JSON.parse(fs.readFileSync("build/corpus_src.json"));
const out = K.map(k => { const r = checkKuralLicensed(k.l1 + "\n" + k.l2); return { ...k, ok: r.ok, error: r.error, detail: r.detail, seers: r.seers }; });
fs.writeFileSync("build/corpus.json", JSON.stringify(out));
console.log("corpus pass", out.filter(k => k.ok).length, "/", out.length);
