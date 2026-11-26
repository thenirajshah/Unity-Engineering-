# Verification report

## Built deliverables

- 63 routable pages and a custom 404. The 63 routes include six equipment categories and all 45 authoritative product entries.
- 90 Blender equipment views, six derived equipment banners, 10 fabrication concepts, four cinematic concepts and 10 equipment detail concepts. Delivery images use WebP. The 45 primary/alternate pairs are separate camera views, with model detail varying by equipment.
- Six on-demand, indexed GLB viewers. The heat exchanger has additional tube-bundle and exploded-assembly assets. The concept visuals illustrate equipment families. Mechanical details require engineering review.
- Nine-page PDF with all 45 catalogue entries, original branding and the supplied business contact information. No capacity, pressure or standards claims were added.
- Dedicated local Git history preserving V1. Cloudflare Pages headers, redirects, deployment instructions and a GitHub Actions quality workflow are included.

## Executed checks

`npm run lint`, `npm run check`, `npm run build` and `npm test` passed. The static test checked 64 HTML documents for unique titles and descriptions, internal references, alternate views, valid GLB envelopes and all 45 PDF entries. A second build with a test HTTPS origin verified 63 sitemap URLs, canonical and robots configuration, and 45 legacy redirects. The deliverable build has preview indexing disabled.

The Playwright suite uses Chromium on a virtual HTTPS origin, without transmitting project test information or sending enquiries. It checks widths of 360, 390, 768, 1024, 1440 and 1920 pixels on the homepage, catalogue, quotation page and a representative product page. It also checks the catalogue search, filtering and preview, mobile menu, legacy contact links, quotation prefill and draft handling, all 45 equipment routes, six category routes, six WebGL viewers, model fallback, the custom 404 and PDF delivery.

## Unverified deployment and asset scope

GitHub repository creation returned `Resource not accessible by integration (createRepository)`. The project is preserved in local Git. Cloudflare Pages account authorization was unavailable, so HTTPS, automatic deployment, production indexing and live verification are pending. See [deployment instructions](DEPLOYMENT.md).

The supplied V1 logo geometry is preserved. Studio and fabrication images are generated or rendered concepts. Fabrication imagery does not depict Unity Engineering’s facility. Standard equipment delivery renders are 640 × 540. Geometry, finishes and process images remain subject to engineering approval before use as equipment documentation. The build uses static Python templates and native WebGL instead of Astro, React, Three.js and GSAP. The homepage loads the 3D scene on request to keep the opening view light.

## Browser outcome and performance

The final offline Chromium run passed, including email and WhatsApp draft formatting, interactive component controls, the heat exchanger's cutaway and exploded views, the blocked-model fallback and actual PDF download. The external apps were intercepted during the test, so the run verified the generated drafts rather than third-party delivery.

At 1440 pixels, the virtual HTTPS run recorded a 336 ms largest contentful paint, 0 cumulative layout shift and 341,910 decoded resource bytes excluding the PDF. This run used local file delivery with browser interception. It did not measure production network behavior, Lighthouse scores, or field INP.

Desktop, tablet and mobile screenshots are included in the delivery package. Production measurement and a full screen-reader audit remain pending.
