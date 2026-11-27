# Unity Engineering V3.0

Static industrial catalogue and business enquiry site for Unity Engineering, Ankleshwar, Gujarat. The site has 23 product details, six equipment categories, a PDF catalogue and five on-demand WebGL equipment viewers.

## Build and verify

Use Node.js 22+ and Python 3.11+. The website build uses Python’s standard library and installs no runtime dependencies.

```sh
npm ci
npm run lint
npm run check
npm run build
npm test
python3 -m http.server 8080 --directory dist
```

The static test uses `pdftotext` from Poppler. The Playwright test serves the build from an intercepted virtual HTTPS origin and needs no server or public domain.

```sh
npm install --no-save --package-lock=false playwright@1.62.1
npx playwright install chromium
node scripts/browser-test.cjs
```

Set `CHROMIUM_PATH` to use an existing Chromium installation. The browser test writes screenshots and metrics to `test-results/`.

## Maintain the catalogue

- Update `src/products.json` for names, descriptions, process principles, applications and features. Keep published slugs stable. Add an explicit redirect if a slug changes.
- Update `src/categories.json` for equipment families. The build checks the agreed inventory of six categories and 23 entries.
- Update `src/pages.json` for company and process content and `src/components.json` for model component notes.
- Use approved operating data or application-specific wording if values are unavailable. Verify photographs and technical geometry before removing concept labels.
- Use `python3 scripts/catalogue.py` with Pillow and ReportLab to regenerate the PDF after any equipment or branding update.
- Run `node scripts/models.cjs` to regenerate the eight GLBs. To render equipment again, run `node scripts/geometry.cjs`, then `blender -b -t 8 -P scripts/render.py` and `python3 scripts/optimize.py` with Pillow installed.
- Maintain [ASSETS.csv](ASSETS.csv) when adding imagery. The primary image is required for every published product. Optional responsive, card, thumbnail and detail-crop paths live alongside the primary in its image record. Regenerate these variants when the primary changes.

The enquiry form prepares a draft locally. Visitors review and send through email or WhatsApp. The website collects no stored submissions, uploads or analytics.

[Deployment](docs/DEPLOYMENT.md) · [V3 audit](docs/WEBSITE_AUDIT.md) · [Test report](docs/TEST_REPORT.md) · [V3 delivery report](docs/FINAL_UPGRADE_REPORT.md) · [Changelog](CHANGELOG.md)
