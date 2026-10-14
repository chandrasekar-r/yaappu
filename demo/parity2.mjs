import { checkKuralLicensed, normalize } from "./build/licensed.mjs";
import fs from "fs";
const cases = JSON.parse(fs.readFileSync(new URL("./build/parity_lic_py.json", import.meta.url)));
let bad = 0;
cases.forEach((c, i) => {
  const r = checkKuralLicensed(c.text);
  const same = r.ok === c.ok && r.error === c.error && r.detail === c.detail && JSON.stringify(r.seers) === JSON.stringify(c.seers) && normalize(c.text) === c.norm;
  if (!same && bad++ < 5) console.log("MISMATCH", i, JSON.stringify(c), JSON.stringify(r));
});
console.log(`licensed checker parity: ${cases.length - bad}/${cases.length} identical`);
process.exit(bad ? 1 : 0);
