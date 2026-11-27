# Unity Engineering V3 test report

## Functional coverage

The production-style static build uses the Cloudflare Pages main-branch configuration. The source checks validate syntax, heading counts, unique metadata, local assets and fragment targets, PDF content and sizing units, redirect destinations and GLB structure. The result contains 43 sitemap URLs and one custom 404. The PDF has all 23 equipment entries with the same technical sizing units as the site.

| Check | Coverage |
| --- | --- |
| Chromium and Playwright | 43 routes at each of 320, 375, 430, 768, 1024, 1440, 1920 and 2560 CSS pixels. Checked heading visibility, response codes, horizontal overflow, page errors and asset HTTP errors. |
| Equipment discovery | Text search, every category filter, no-results state, clear filters, keyboard mega menu, mobile drawer and category navigation. |
| Product media | Primary image decoding for 23 products, component crop selection, keyboard dismissal of zoom and five interactive model routes. The exchanger tube bundle and exploded modes, zoom, reset, component focus, auto-rotation and a forced failed-GLB fallback were exercised. |
| Enquiries | Product-prefilled RFQ links on all detail routes, working volume in kL, requirements validation, direct WhatsApp enquiry and draft message contents. The test intercepts email and WhatsApp draft destinations locally. |
| Document and metadata | PDF download and content type, a 404 response for a missing route, all canonical pages and published redirect mappings. |
| Firefox | Seven routes at 375 and 1440px, desktop and mobile navigation, image decoding, filtering, zoom dialog and kL quotation prefill. |
| Accessibility | Zero violations in 32 automated axe checks across 16 routes at 375 and 1440px, keyboard navigation and reduced-motion browser assertions. Safari and assistive hardware were outside the available test coverage. |

## Lighthouse comparison

One paired navigation run per form factor with Lighthouse 13.6.0 on local HTTP, comparing the previous deployed source and optimized V3 using equivalent presets. Transfer sizes cover the sampled homepage navigation. They are distinct from the entire static build. Mobile uses Lighthouse simulated throttling.

| Build and viewport preset | Performance | Accessibility | Best practices | SEO | LCP | CLS | TBT | Transfer |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| V2.2 desktop | 100 | 100 | 100 | 100 | 0.49 s | 0.000 | 0 ms | 327 KiB |
| V3 desktop | 100 | 100 | 100 | 100 | 0.55 s | 0.001 | 0 ms | 286 KiB |
| V2.2 mobile | 99 | 100 | 100 | 100 | 2.19 s | 0.000 | 12.5 ms | 318 KiB |
| V3 mobile | 97 | 100 | 100 | 100 | 2.48 s | 0.000 | 70 ms | 266 KiB |

The V3 snapshot met the target Lighthouse scores and synthetic LCP and CLS thresholds. Mobile remained slower than the previous baseline in this paired run despite transferring fewer bytes. Earlier testing revealed a mobile render bottleneck. The optimization reduced layered masking and hero animation on small screens, preloaded the portrait image and delivered a smaller header logo. No real-user INP or field Core Web Vitals were measured.

## Screenshot evidence

The delivery folder contains before and after captures for the homepage, catalogue, reactor detail, fabrication and shell-and-tube assembly. V3 also includes engineering, quotation and additional mobile captures. Visual inspection addressed first-viewport legibility, mobile cropping, product silhouette framing and the technical detail layout.

## Production checks

The Cloudflare Pages deployment uses the GitHub `main` branch. Release verification probes the HTTPS origin, canonical route inventory, redirects, error status, security headers and byte-level matches for release assets. The accompanying delivery stores the live request evidence alongside screenshots and Lighthouse output.
