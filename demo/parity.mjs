// Compare TS checker with Python on every case in build/parity_py.json; exit 1 on any mismatch.
import { checkKural } from "./build/checker.mjs";
import fs from "fs";
const cases = JSON.parse(fs.readFileSync(new URL("./build/parity_py.json", import.meta.url)));
let bad = 0, raw = 0;
cases.forEach((c, i) => {
  const r = checkKural(c.text);
  const same = r.ok === c.ok && r.error === c.error && r.detail === c.detail && JSON.stringify(r.seers) === JSON.stringify(c.seers);
  if (i < 1330 && same) raw++;
  if (!same && bad++ < 5) console.log("MISMATCH", i, JSON.stringify(c), JSON.stringify(r));
});
console.log(`raw kurals: ${raw}/1330 identical; all cases: ${cases.length - bad}/${cases.length} identical`);
process.exit(bad ? 1 : 0);
