// node shots.js (run from a dir with playwright installed): desktop + mobile, light + dark checker
const { chromium } = require("playwright");
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME || undefined });
  const U = "https://yaappu.rclabs.in", out = "/workspace/yaappu/demo/shots/";
  const pages = [["checker", "/"], ["checker-broken", "/#" + encodeURIComponent("அகர முதல எழுத்தெல்லாம் ஆதி\nபகவன் கருவிளங்கனி உலகு.")], ["corpus", "/corpus"], ["gallery", "/gallery"], ["about", "/about"]];
  for (const [dev, vp] of [["desktop", { width: 1366, height: 900 }], ["mobile", { width: 390, height: 844, isMobile: true, deviceScaleFactor: 2 }]]) {
    for (const theme of ["light", "dark"]) {
      const ctx = await b.newContext({ viewport: { width: vp.width, height: vp.height }, isMobile: !!vp.isMobile, deviceScaleFactor: vp.deviceScaleFactor || 1, colorScheme: theme });
      const p = await ctx.newPage();
      for (const [name, path] of pages) {
        if (theme === "dark" && !["checker", "corpus"].includes(name)) continue;
        await p.goto("about:blank"); await p.goto(U + path, { waitUntil: "networkidle" });
        await p.waitForTimeout(600);
        await p.screenshot({ path: `${out}${name}-${dev}-${theme}.png`, fullPage: name !== "corpus" && name !== "gallery" || dev === "desktop" ? false : false });
      }
      await ctx.close();
    }
  }
  await b.close();
})();
