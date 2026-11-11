// Lebriz Müzayede Bilgi Bankası koruma kopyası (sahibe özel; yayın Lebriz iznine tabi).
// Gerçek tarayıcıyla (Playwright Chromium) çalışır. Giriş bilgisi dosyada tutulmaz:
// Lebriz'in giriş sayfasında kamuya açık yazdığı arşiv hesabı sayfadan okunur.
// Kullanım: node muzayede_cek.js <koruma_dizini> <saat>   (DELAY_MS ortam değişkeni)
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), zlib = require('zlib');
const ROOT = process.argv[2], MAXH = parseFloat(process.argv[3] || '1.7');
const DELAY = parseInt(process.env.DELAY_MS || '1000');
const OUT = path.join(ROOT, 'muzayede'), SAY = path.join(OUT, 'sayfalar');
fs.mkdirSync(SAY, { recursive: true });
const MAN = path.join(OUT, 'manifest.tsv'), ERR = path.join(OUT, 'hatalar.tsv');
const BASE = 'http://lebriz.com/pages/';
const sleep = ms => new Promise(r => setTimeout(r, ms));
const now = () => new Date().toISOString().slice(0, 19);
const wait = () => sleep(DELAY + Math.random() * 1000);
function save(aid, pg, html) {
  const d = path.join(SAY, String(parseInt(aid) % 100).padStart(2, '0'));
  let f = path.join(d, `${aid}-${pg}.html.gz`);
  try { fs.mkdirSync(d, { recursive: true }); } catch (e) { f = path.join(SAY, `${aid}-${pg}.html.gz`); } // yeni dizin açılamazsa düz
  fs.writeFileSync(f + '.tmp', zlib.gzipSync(html)); fs.renameSync(f + '.tmp', f);
}
async function login(page) {
  await wait();
  await page.goto(BASE + 'login.aspx?lang=TR&ReturnURL=%2fpages%2fauction_DB.aspx%3flang%3dTR%26bhcp%3d1', { timeout: 240000 });
  await page.waitForSelector('#login_txtEmailStd', { timeout: 240000 }); await page.waitForLoadState('load');
  const txt = await page.evaluate(() => document.body.innerText);
  const m = txt.match(/Email adresi:\s*(\S+@\S+)\s+ve şifre:\s*(\S+)\s+yazarak/);
  if (!m) throw new Error('DUR: giriş sayfasında kamuya açık arşiv hesabı yok');
  await page.fill('#login_txtEmailStd', m[1]); await page.fill('#login_txtPassStd', m[2]);
  await Promise.all([page.waitForNavigation({ timeout: 240000 }), page.click('#login_butSubmitStd')]);
  if (!/auction_DB/.test(page.url())) throw new Error('DUR: giriş başarısız');
}
(async () => {
  const done = new Set();
  if (fs.existsSync(MAN)) for (const l of fs.readFileSync(MAN, 'utf8').split('\n')) { const f = l.split('\t'); if (f[3] === 'tamam') done.add(f[1]); }
  // en çok kaydı olan sanatçılar önce (kapanma riskine karşı)
  const ids = fs.readFileSync(path.join(ROOT, 'muzayede-sanatci-listesi.csv'), 'utf8').split('\n').slice(1).filter(Boolean)
    .map(l => { const f = l.split(','); return [f[0], parseInt(f[f.length - 1]) || 0]; }).sort((a, b) => b[1] - a[1]).map(x => x[0]);
  // TEKRAR=id,id,... : 4 Kasım dizin hatasında sayfaları kaybolan sanatçıları yeniden çek (2026-11-11)
  const todo = process.env.TEKRAR ? process.env.TEKRAR.split(',') : ids.filter(i => !done.has(i));
  console.log(`tamam=${done.size} kalan=${todo.length}`);
  const browser = await chromium.launch(); const page = await browser.newPage();
  await login(page);
  const end = Date.now() + MAXH * 3600e3; let n = 0;
  for (const aid of todo) {
    if (Date.now() > end) break;
    const u = BASE + `auction_DB.aspx?lang=TR&bhcp=1&results=artist&aucID=0&sanatciID=${aid}&sortBy=price&sortDir=DESC`;
    let ok = true, pages = 0;
    try {
      await wait(); await page.goto(u, { timeout: 240000 });
      if (/login\.aspx|cookieMonster/.test(page.url())) { await login(page); await wait(); await page.goto(u, { timeout: 240000 }); }
      if (/login\.aspx|cookieMonster/.test(page.url())) throw new Error('DUR: sunucu girişi kabul etmiyor');
      let html = await page.content(); save(aid, 1, html); pages = 1;
      const lab = await page.$eval('#aucDB_awv_pager1_tdLabels1', e => e.innerText).catch(() => '');
      const mm = lab.match(/Sayfa\s*:\s*(\d+)\s*\/\s*(\d+)/); const N = mm ? parseInt(mm[2]) : 1;
      for (let pg = 2; pg <= N; pg++) {
        let got = false;
        for (let att = 0; att < 3 && !got; att++) {
          try {
            await wait();
            await Promise.all([page.waitForNavigation({ timeout: 240000 }), page.click('#aucDB_awv_pager1_butRight')]);
            const lab2 = await page.$eval('#aucDB_awv_pager1_tdLabels1', e => e.innerText).catch(() => '');
            const m2 = lab2.match(/Sayfa\s*:\s*(\d+)\s*\//);
            if (m2 && parseInt(m2[1]) !== pg) throw new Error(`sayfa uyuşmuyor ${m2[1]}!=${pg}`);
            save(aid, pg, await page.content()); pages++; got = true;
          } catch (e) { fs.appendFileSync(ERR, `${now()}\t${aid}-${pg}\t${String(e.message).slice(0, 120)}\n`); await sleep(10000); }
        }
        if (!got) { ok = false; break; }
      }
    } catch (e) {
      if (String(e.message).startsWith('DUR')) { console.log(e.message); await browser.close(); process.exit(2); }
      ok = false; fs.appendFileSync(ERR, `${now()}\t${aid}\t${String(e.message).slice(0, 120)}\n`);
    }
    fs.appendFileSync(MAN, `${now()}\t${aid}\t${pages}\t${ok ? 'tamam' : 'eksik'}\n`); n++;
    if (n % 50 === 0) console.log(`${now()} sanatci=${n} toplam_tamam=${done.size + n}`);
  }
  console.log(`BITTI sanatci=${n}`); await browser.close();
})();
