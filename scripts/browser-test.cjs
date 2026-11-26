/* Test built documents using a virtual HTTPS origin. No servers or network needed. */
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const products = require('../src/products.json');

const origin = 'https://unity-engineering.test';
const types = {
  '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css',
  '.webp': 'image/webp', '.png': 'image/png', '.glb': 'model/gltf-binary',
  '.pdf': 'application/pdf', '.woff2': 'font/woff2'
};

async function run() {
  fs.mkdirSync('test-results', { recursive:true });
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH || undefined,
    args: ['--enable-webgl','--use-angle=swiftshader','--enable-unsafe-swiftshader']
  });
  const context = await browser.newContext({ reducedMotion: 'reduce' });
  const errors = [];
  const headerConfig = fs.readFileSync('public/_headers','utf8').split('\n').slice(1).filter(Boolean);
  const securityHeaders = Object.fromEntries(headerConfig.map((line) => {
    const colon = line.indexOf(':');
    return [line.slice(0,colon).trim(),line.slice(colon + 1).trim()];
  }));
  await context.addInitScript(() => {
    window.lab = { lcp:null, shifts:0 };
    new PerformanceObserver(list => {
      window.lab.lcp = list.getEntries().at(-1)?.startTime ?? window.lab.lcp;
    }).observe({type:'largest-contentful-paint',buffered:true});
    new PerformanceObserver(list => {
      for (const entry of list.getEntries()) if (!entry.hadRecentInput) window.lab.shifts += entry.value;
    }).observe({type:'layout-shift',buffered:true});
  });
  await context.route(origin + '/**', async (route) => {
    const routePath = new URL(route.request().url()).pathname;
    const name = path.resolve('dist', '.' + routePath);
    const file = routePath.endsWith('/') ? path.join(name, 'index.html') : name;
    if (!fs.existsSync(file) || !fs.statSync(file).isFile()) {
      return route.fulfill({ path: 'dist/404.html', status:404, contentType:'text/html' });
    }
    return route.fulfill({ path: file, contentType: types[path.extname(file)], headers: { ...securityHeaders, 'content-length':String(fs.statSync(file).size) } });
  });
  const page = await context.newPage();
  page.setDefaultTimeout(12000);
  page.on('pageerror', (error) => errors.push(String(error)));
  for (const width of [360,390,768,1024,1440,1920]) {
    await page.setViewportSize({width, height:900});
    for (const route of ['/', '/products/', '/quotation/', '/products/limpet-coil-reactors/']) {
      await page.goto(origin + route);
      assert(await page.locator('h1').isVisible(), route);
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `Overflow at ${width} on ${route}`);
    }
    if ([390,768,1440].includes(width)) {
      await page.goto(origin + '/');
      await page.locator('.hero-art img').evaluate(image => image.decode());
      await page.screenshot({path:`test-results/home-${width}.png`});
    }
  }
  await page.setViewportSize({width:390,height:844});
  await page.goto(origin);
  await page.getByRole('button',{name:'Menu',exact:true}).click();
  await page.locator('.mega summary').click();
  assert(await page.locator('.mega-grid a.menu-cat').count() === 6);
  await page.keyboard.press('Escape');
  await page.keyboard.press('Escape');
  assert.equal(await page.getByRole('button',{name:'Menu',exact:true}).getAttribute('aria-expanded'), 'false');

  await page.setViewportSize({width:1440,height:950});
  await page.goto(origin + '/products/');
  await page.locator('.card img').evaluateAll(images => Promise.all(images.slice(0,3).map(image => image.decode())));
  await page.screenshot({path:'test-results/catalogue-1440.png'});
  await page.locator('#search').fill('Limpet coil');
  assert.equal(await page.locator('#count').textContent(),'1 equipment entry');
  await page.locator('.card:visible .preview').click();
  assert(await page.getByRole('dialog').isVisible());
  await page.keyboard.press('Escape');
  await page.locator('#category').selectOption('4');
  assert(await page.locator('#no-results').isVisible());
  await page.locator('#search').fill('');
  assert.equal(await page.locator('#count').textContent(),'12 equipment entries');
  await page.goto(origin + '/quotation/?equipment=limpet-coil-reactors');
  assert.equal(await page.locator('#equipment-name').inputValue(),'limpet-coil-reactors');
  assert.equal(await page.locator('#equipment-category').inputValue(),'0');
  assert.equal(await page.locator('form').evaluate(form => form.checkValidity()), false);
  await page.locator('#equipment-category').selectOption('1');
  assert.equal(await page.locator('#equipment-name').inputValue(),'');
  for (const [field,value] of Object.entries({name:'Testing',company:'Sample Company',email:'qa@example.test',phone:'+919999999999',requirements:'Example enquiry only'})) {
    await page.locator('#'+field).fill(value);
  }
  await page.evaluate(() => { window.open = (url) => { window.draftUrl = url; }; });
  await page.getByRole('button',{name:'Open WhatsApp draft'}).click();
  const draft = new URL(await page.evaluate(() => window.draftUrl));
  assert.equal(draft.origin + draft.pathname,'https://wa.me/919934969351');
  assert(draft.searchParams.get('text').includes('Example enquiry only'));
  await page.evaluate(() => {
    const click = HTMLAnchorElement.prototype.click;
    HTMLAnchorElement.prototype.click = function () {
      if (this.protocol === 'mailto:') window.emailDraft = this.href;
      else click.call(this);
    };
  });
  await page.getByRole('button',{name:'Open email draft'}).click();
  const emailDraft = new URL(await page.evaluate(() => window.emailDraft));
  assert.equal(emailDraft.pathname,'Nirajkumarshah17@gmail.com');
  assert(emailDraft.searchParams.get('body').includes('Example enquiry only'));
  assert.equal(await page.locator('#form-status').textContent(),'Review and send the draft in your email app.');
  assert.equal(await page.locator('a[href^="tel:"]').first().getAttribute('href'),'tel:+919934969351');
  assert.equal(await page.locator('a[href^="mailto:"]').first().getAttribute('href'),'mailto:Nirajkumarshah17@gmail.com');

  const viewers = ['reactor-limpet','exchanger','pressure','anfd','ribbon','rmg'];
  for (const p of products) {
    const response = await page.goto(origin + '/products/' + p.slug + '/');
    assert.equal(response.status(),200);
    assert.equal(await page.locator('h1').textContent(),p.title);
    if (!viewers.includes(p.kind)) continue;
    await page.getByRole('button',{name:'Launch interactive 3D'}).click();
    await page.locator('.viewer.running').waitFor({timeout:12000});
    await page.getByRole('button',{name:'Zoom in'}).click();
    await page.locator('canvas:visible').press('ArrowRight');
    await page.getByRole('button',{name:'Reset'}).click();
    const component = page.locator('[data-component]').first();
    await component.click();
    assert.equal(await component.getAttribute('aria-pressed'),'true');
    assert((await page.locator('.component-note').textContent()).length > 20);
    await page.getByRole('button',{name:'Auto-rotate'}).click();
    assert.equal(await page.getByRole('button',{name:'Auto-rotate'}).getAttribute('aria-pressed'),'true');
    if (p.kind === 'exchanger') {
      const toggle = page.getByRole('button',{name:'Tube bundle'});
      await toggle.click();
      await page.waitForFunction(() => document.querySelector('[data-control="cutaway"]').getAttribute('aria-pressed') === 'true');
      const exploded = page.getByRole('button',{name:'Exploded assembly'});
      await exploded.click();
      await page.waitForFunction(() => document.querySelector('[data-control="exploded"]').getAttribute('aria-pressed') === 'true');
      assert.equal(await toggle.getAttribute('aria-pressed'),'false');
      await page.locator('.viewer').screenshot({path:'test-results/exchanger-3d.png'});
    }
  }
  await page.route('**/assets/models/*.glb', route => route.abort());
  await page.goto(origin + '/products/limpet-coil-reactors/');
  await page.getByRole('button',{name:'Launch interactive 3D'}).click();
  await page.locator('.viewer-status').getByText('Interactive 3D is unavailable. Showing the concept image.').waitFor();
  assert(await page.locator('.viewer-still').isVisible());
  for (const [slug] of require('../src/categories.json')) {
    assert.equal((await page.goto(origin + '/products/categories/' + slug + '/')).status(),200);
  }
  assert.equal((await page.goto(origin + '/missing')).status(),404);
  await page.goto(origin + '/catalogue/');
  const pendingDownload = page.waitForEvent('download');
  await page.getByRole('link',{name:'Download equipment catalogue PDF'}).click();
  const downloaded = await pendingDownload;
  assert.equal(downloaded.suggestedFilename(),'catalogue.pdf');
  await page.goto(origin);
  await page.locator('.hero-art img').evaluate(image => image.decode());
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  const pdf = await page.evaluate(async () => {
    const response = await fetch('/assets/catalogue.pdf');
    return { type:response.headers.get('content-type'), magic:new TextDecoder().decode((await response.arrayBuffer()).slice(0,5)) };
  });
  assert.deepEqual(pdf,{type:'application/pdf',magic:'%PDF-'});
  assert.deepEqual(errors, []);
  const timing = await page.evaluate(() => ({
    lcpMilliseconds: Math.round(window.lab.lcp),
    cumulativeLayoutShift: window.lab.shifts,
    decodedResourceBytes: performance.getEntriesByType('resource').filter(entry => !entry.name.endsWith('.pdf')).reduce((sum, entry) => sum + entry.decodedBodySize, 0),
    heroImagePixels: document.querySelector('.hero-art img').naturalWidth,
    viewport: innerWidth
  }));
  fs.writeFileSync('test-results/browser-metrics.json',JSON.stringify(timing,null,2));
  console.log('Chromium passed responsive layout, navigation, products, categories, catalogue search, quotation draft, six GLBs, component views, cutaway, exploded assembly, fallback, 404 and PDF checks.');
  await browser.close();
}
run().catch((error) => { console.error(error); process.exit(1); });
