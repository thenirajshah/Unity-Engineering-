# V2.2 website audit

Baseline commit `0990077`, production at `unity-engineering.pages.dev`. Reviewed the static generator, structured catalogue and sizing data, frontend, 3D runtime, PDF tooling, asset manifest, deployment and CI files. The resulting inventory contained 42 canonically addressable routes and the custom 404.

| Priority | Area | Finding |
| --- | --- | --- |
| Critical | Availability | No critical availability break reproduced. All 42 live routes, PDF, sitemap and robots returned HTTP 200. An unknown path returned HTTP 404. |
| High | Homepage | The top fold relies on a generic dark composition and the catalogue uses six similar tiles. Company positioning, featured equipment and quality have limited space and hierarchy. |
| High | Product media | Each product relies on one approved concept still. Most source frames are about 440 pixels per side. A wide card crop can obscure equipment supports or fittings. The site has no approved factory photo library. |
| High | Product path | Users must read through the introduction and filters before reaching the first equipment row. Detail pages repeat the same section density, and direct WhatsApp context is available only through the form. |
| Medium | Motion and 3D | Hero entry and hover transitions exist. The site has limited scroll feedback or staged fabrication storytelling. Five GLB viewers and exchanger assembly modes passed baseline interactions. Existing concept models remain illustrative. |
| Medium | Responsive and access | The site has semantic controls and a focusable 3D viewer. The desktop menu needs clearer direct equipment links. Gallery images lack zoom. System font fallbacks determine the baseline typography. |
| Medium | Engineering content | Available sizing units are useful. Verified model capacity data, specific in-house capabilities and actual project photography are missing. Keep scope conditional and use the quote form for customer requirements. |
| Medium | SEO | Unique titles and descriptions, organization and breadcrumb schema, a production sitemap and robots handling exist. Improve linking between engineering information, application and product routes. Use a production-specific social image. |
| Low | Hosting | Git-integrated Cloudflare Pages, redirects, browser content policy and no-index preview behavior work. The pipeline requires Python, Node and a PDF text extraction check. |

## Baseline measurements

The production-style local build was 7,600,795 bytes across the output tree. One headless desktop Chromium run at 1440px recorded 612 ms LCP, 0 CLS and 295,659 decoded resource bytes during the observation window. The raster hero request used a 1536px image. These local figures do not represent field Core Web Vitals. The Playwright suite exercised catalogue, quotation drafts, five 3D viewers, fallbacks and the PDF. Before captures are in the V3 delivery folder.
