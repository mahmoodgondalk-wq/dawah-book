// Fetch hadith English text from sunnah.com with headless Chromium (the site is behind a JS challenge).
// Usage: NODE_PATH=$(npm root -g) node fetch_sunnah.js bukhari:2440 muslim:2807 ...
// Saves output_final/work/references/hadith_<collection>_<number>.json
// The English text is taken verbatim (innerText) from the hadith's English container as displayed:
// narrator line (.hadith_narrated) and text (.text_details), plus the page's own reference table.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const REFDIR = path.join(__dirname, '..', 'references');

(async () => {
  const refs = process.argv.slice(2);
  const browser = await chromium.launch({
    headless: true,
    proxy: process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined,
    args: ['--ignore-certificate-errors'],
  });
  const ctx = await browser.newContext({
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
  });
  const page = await ctx.newPage();
  for (const ref of refs) {
    const [coll, num] = ref.split(':');
    const out = path.join(REFDIR, `hadith_${coll}_${num.replace(/[^0-9a-z]/gi, '_')}.json`);
    if (fs.existsSync(out)) { console.log(ref, 'exists'); continue; }
    const url = `https://sunnah.com/${coll}:${num}`;
    try {
      let resp = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 90000 });
      for (let i = 0; i < 20; i++) {
        const t = await page.title();
        if (!/moment/i.test(t)) break;
        await page.waitForTimeout(2000);
      }
      await page.waitForTimeout(800);
      const data = await page.evaluate(() => {
        const boxes = Array.from(document.querySelectorAll('.actualHadithContainer'));
        return {
          title: document.title,
          finalUrl: location.href,
          hadiths: boxes.map(b => {
            const eng = b.querySelector('.englishcontainer');
            const nar = eng ? eng.querySelector('.hadith_narrated') : null;
            const det = eng ? eng.querySelector('.text_details') : null;
            const reft = b.querySelector('.hadith_reference');
            return {
              narrated: nar ? nar.innerText.trim() : '',
              text: det ? det.innerText.trim() : '',
              english_full: eng ? eng.innerText.trim() : '',
              reference_table: reft ? reft.innerText.trim() : '',
            };
          }),
        };
      });
      const doc = { kind: 'hadith', ref: ref, url: url, final_url: data.finalUrl, page_title: data.title,
        retrieved_utc: new Date().toISOString().replace(/\.\d+Z$/, 'Z'), hadiths: data.hadiths };
      fs.writeFileSync(out + '.raw', JSON.stringify(doc, null, 1));
      console.log(ref, 'fetched', data.hadiths.length, 'hadith box(es)', '|', data.title.slice(0, 80));
    } catch (e) {
      console.log(ref, 'FAILED', String(e).slice(0, 200));
    }
    await page.waitForTimeout(1500);
  }
  await browser.close();
})();
