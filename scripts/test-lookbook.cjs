const assert = require('node:assert/strict');
const products = require('../src/products.json');
const categories = require('../src/categories.json');

const selection = ['reactor-limpet', 'exchanger', 'column', 'pressure', 'anfd', 'ribbon']
  .map(kind => products.find(product => product.kind === kind));

async function expectEquipment(page, i) {
  const p = selection[i];
  const detail = page.locator('.lineup-detail:visible');
  await page.locator('.lineup-ready').waitFor();
  assert.equal(await detail.count(), 1);
  assert.equal(await detail.locator('h2').innerText(), p.title);
  assert.deepEqual(await detail.locator('dd').allTextContents(), [p.application, p.features]);
  assert.equal(await detail.locator('.lineup-description').textContent(), p.desc);
  assert.equal(await page.locator('.lineup-index [aria-current]').textContent(), categories[p.cat][1]);
  assert.equal(await page.locator('.lineup-count b').innerText(), String(i + 1).padStart(2, '0'));
  assert.equal(await page.locator('.lineup-machine[data-slot="0"] img').getAttribute('src'), '/assets/' + p.approved_image.asset);
  assert.equal(await page.locator('.lineup-credit:visible').innerText(), p.approved_image.label);
  assert.equal(await detail.getByRole('link', { name: 'View equipment' }).getAttribute('href'), '/products/' + p.slug + '/');
  assert.equal(await detail.getByRole('link', { name: 'Request quotation' }).getAttribute('href'), '/quotation/?equipment=' + p.slug);
}

async function capture(page, name) {
  await page.evaluate(async () => {
    await document.fonts.ready;
    await Promise.all([...document.querySelectorAll('.lineup-machine img')].map(img => img.decode()));
    await Promise.all(document.querySelector('.lineup').getAnimations({ subtree: true }).map(a => a.finished));
  });
  await page.screenshot({ path: 'test-results/lookbook-' + name + '.png' });
}

module.exports = async function testLookbook({ browser, page, origin, serveBuiltFile }) {
  const path = '/equipment-lookbook/';
  const next = page.getByRole('button', { name: 'Next equipment' });
  const previous = page.getByRole('button', { name: 'Previous equipment' });
  const stage = page.locator('.lineup-stage');
  await page.setViewportSize({ width: 1440, height: 810 });
  await page.goto(origin);
  await page.locator('.feature-band').getByRole('link', { name: 'Open equipment lookbook' }).click();
  assert.equal(new URL(page.url()).pathname, path);
  await page.goto(origin);
  await page.locator('.mega summary').click();
  await page.locator('.mega').getByRole('link', { name: 'Equipment lookbook' }).click();
  await expectEquipment(page, 0);

  for (const [width, height] of [[1440,810], [2560,1440], [820,1000], [390,844]]) {
    await page.setViewportSize({ width, height });
    for (const [index] of selection.entries()) {
      if (index) await next.click();
      const geometry = await page.evaluate(() => {
        const rect = selector => document.querySelector(selector).getBoundingClientRect().toJSON();
        const img = document.querySelector('.lineup-machine[data-slot="0"] img');
        return {
          image: img.getBoundingClientRect().toJSON(), aspect: img.naturalWidth / img.naturalHeight,
          stage: rect('.lineup-stage'), controls: rect('.lineup-controls'), title: rect('.lineup-detail:not([hidden]) h2'),
          quote: rect('.lineup-detail:not([hidden]) .actions a'), overflow: document.documentElement.scrollWidth - innerWidth
        };
      });
      const { image, aspect, controls, title, quote, overflow } = geometry;
      assert.equal(overflow, 0, 'Horizontal overflow at ' + width);
      assert(Math.abs(image.width / image.height - aspect) < .01);
      assert(image.x >= geometry.stage.x && image.right <= geometry.stage.right + 1);
      assert(image.y >= geometry.stage.y && image.bottom <= geometry.stage.bottom + 1);
      if (width > 820) {
        assert(image.x > title.right && image.width >= 470, 'Prominent foreground plate beside details');
        if (width === 1440) assert(Math.max(quote.bottom, image.bottom, controls.bottom, title.bottom) <= height, selection[index].title + ' exceeds viewport: ' + JSON.stringify(geometry));
      } else {
        assert(image.bottom <= controls.top && controls.bottom <= title.y);
        assert(controls.bottom <= height, 'Controls immediately accessible on mobile');
      }
    }
    await next.click();
    await expectEquipment(page, 0);
  }

  await page.setViewportSize({ width: 1440, height: 810 });
  await page.goto(origin + path);
  await capture(page, 'desktop-reactor');
  await next.click();
  await expectEquipment(page, 1);
  await page.mouse.move(0, 0);
  await capture(page, 'desktop-exchanger');

  for (const [index, p] of selection.entries()) {
    await page.locator('.lineup-index a').nth(index).click();
    await expectEquipment(page, index);
    await page.locator('.lineup-detail:visible').getByRole('link', { name: 'Request quotation' }).click();
    assert.equal(await page.locator('#equipment-name').inputValue(), p.slug);
    assert.equal(await page.locator('#equipment-category').inputValue(), String(p.cat));
    await page.goto(origin + path);
    await page.locator('.lineup-index a').nth(index).click();
    await page.locator('.lineup-detail:visible').getByRole('link', { name: 'View equipment' }).click();
    assert.equal(await page.locator('h1').innerText(), p.title);
    await page.goto(origin + path);
  }

  await stage.focus();
  await page.keyboard.press('ArrowLeft');
  await expectEquipment(page, 5);
  await page.keyboard.press('ArrowRight');
  await expectEquipment(page, 0);
  await previous.click();
  await expectEquipment(page, 5);
  await next.click();
  await expectEquipment(page, 0);

  // Sample the exposed area of each receding plate and send a real pointer click.
  for (let depth = 1; depth < selection.length; depth++) {
    await page.locator('.lineup-index a').first().click();
    const point = await page.locator(`.lineup-machine[data-slot="${depth}"]`).evaluate(el => {
      const box = el.getBoundingClientRect();
      const y = box.y + box.height / 2;
      for (let x = box.right - 2; x > box.x; x -= 2) {
        if (el.contains(document.elementFromPoint(x, y))) return { x, y };
      }
      return null;
    });
    assert(point, 'Visible and clickable background plate ' + depth);
    await page.mouse.click(point.x, point.y);
    await expectEquipment(page, depth);
  }

  await page.emulateMedia({ reducedMotion: 'no-preference' });
  let expected = 5;
  for (const direction of [1, 1, -1, 1, -1, -1, -1, 1]) {
    const control = direction === 1 ? next : previous;
    const box = await control.boundingBox();
    await page.mouse.click(box.x + 24, box.y + 24);
    expected = (expected + direction + selection.length) % selection.length;
    await expectEquipment(page, expected);
  }
  // Issue switches before the browser can paint. Each quotation must already agree with its plate.
  const snapshots = await page.evaluate(() => {
    return [1, 1, -1, -1, 1, -1].map(step => {
      document.querySelector(`[data-step="${step}"]`).click();
      return [
        document.querySelector('[data-slot="0"] img').getAttribute('src'),
        document.querySelector('.lineup-detail:not([hidden]) .actions a').getAttribute('href')
      ];
    });
  });
  for (const [i, delta] of [1, 1, -1, -1, 1, -1].entries()) {
    expected = (expected + delta + selection.length) % selection.length;
    const p = selection[expected];
    assert.deepEqual(snapshots[i], ['/assets/' + p.approved_image.asset, '/quotation/?equipment=' + p.slug]);
  }
  await page.evaluate(() => Promise.all(document.querySelector('.lineup').getAnimations({ subtree: true }).map(a => a.finished)));
  assert.equal(await stage.evaluate(el => el.getAnimations({ subtree: true }).length), 0);
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await next.click();
  assert.equal(await stage.evaluate(el => el.getAnimations({ subtree: true }).length), 0);
  expected = (expected + 1) % selection.length;
  const box = await stage.boundingBox();
  const x = box.x + box.width / 3, y = box.y + box.height / 2;
  await page.mouse.move(x, y);
  await page.mouse.down();
  await page.mouse.move(x - 115, y + 6, { steps: 5 });
  await page.mouse.up();
  expected = (expected + 1) % selection.length;
  await expectEquipment(page, expected);
  const before = await page.evaluate(() => scrollY);
  await page.mouse.wheel(0, 320);
  await page.waitForFunction(start => scrollY > start, before);
  await expectEquipment(page, expected);

  const mobile = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  await mobile.route(origin + '/**', serveBuiltFile);
  const phone = await mobile.newPage();
  await phone.goto(origin + path);
  await capture(phone, 'mobile-reactor');
  const touch = await mobile.newCDPSession(phone);
  const swipe = async (from, to) => {
    await touch.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [from] });
    for (let i = 1; i <= 5; i++) {
      const point = { x: from.x + (to.x-from.x)*i/5, y: from.y + (to.y-from.y)*i/5 };
      await touch.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [point] });
    }
    await touch.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
  };
  const photo = await phone.locator('.lineup-machine[data-slot="0"]').boundingBox();
  const center = { x: photo.x + photo.width / 2, y: photo.y + photo.height / 2 };
  await swipe(center, { x: center.x - 110, y: center.y + 3 });
  await expectEquipment(phone, 1);
  await swipe(center, { x: center.x + 110, y: center.y });
  await expectEquipment(phone, 0);
  await swipe(center, { x: center.x, y: center.y - 130 });
  await phone.waitForFunction(() => scrollY > 0);
  await expectEquipment(phone, 0);
  await mobile.close();

  const staticContext = await browser.newContext({ javaScriptEnabled: false });
  await staticContext.route(origin + '/**', serveBuiltFile);
  const staticPage = await staticContext.newPage();
  await staticPage.goto(origin + path);
  assert.equal(await staticPage.locator('.lineup-detail:visible').count(), selection.length);
  assert.equal(await staticPage.locator('.lineup-controls:visible').count(), 0);
  for (const p of selection) {
    const article = staticPage.locator('#look-' + p.kind);
    assert(await article.getByRole('img').isVisible());
    assert(await article.getByRole('heading', { name: p.title }).isVisible());
    assert.equal(await article.getByRole('link', { name: 'Request quotation' }).getAttribute('href'), '/quotation/?equipment=' + p.slug);
    assert.equal(await article.getByRole('link', { name: 'View equipment' }).getAttribute('href'), '/products/' + p.slug + '/');
  }
  await staticContext.close();
  console.log('Lookbook passed four viewport checks, six product and quotation destinations, direct selection, rapid reversal, keyboard, drag, touch, vertical scroll, reduced motion and no-JavaScript checks.');
};
