# Unity Engineering — Industrial website

Static, dependency-free website for Unity Engineering, established 2006. Includes the home page, 45 product pages, original procedural equipment illustrations, interactive WebGL model viewer, and 360° image turntable fallback for six featured products. All images are locally included. No external assets, SVG, paid libraries, analytics, or API keys are required. No database or installation is required.

## Free hosting: Cloudflare Pages (recommended)
1. Extract the ZIP. The directory with `index.html`, `assets`, and `products` is the website root.
2. Log in at https://dash.cloudflare.com/ and open Workers & Pages. Create a Pages project via Direct Upload, then upload the website directory or its ZIP (ensure `index.html` is at the root). Name the project `unity-engineering` if available.
3. Deploy. Cloudflare provides a free `*.pages.dev` address and HTTPS. No custom domain is necessary. Free plan limits and terms apply.
4. Alternative: create a GitHub repository, upload the extracted files, then create a Cloudflare Pages project via Git integration. Use framework preset **None**, no build command, and output directory `.`. GitHub is used for source control, not commercial site hosting. Use a private repository if desired.
5. Netlify can also deploy the same root on its free plan, subject to credits/limits.

## Local preview
Open `index.html` after extracting, or run `python -m http.server 8080` inside the website root and visit http://localhost:8080. A browser with WebGL is recommended. Six featured products also have a 12-frame 360° fallback for browsers without WebGL; other products fall back to their static renders.

## Features
- 6 categories, 45 individually linked equipment pages, product search and filtering.
- WebGL procedural models (drag, keyboard, zoom, reset); 12-angle turntables for the six featured models on unsupported browsers.
- Responsive layout, original uploaded logo, orange industrial design, product-specific enquiry selection, email/WhatsApp/call/map links.
- On-page title and description metadata and static crawlable product URLs. Configure canonical URLs and sitemap when the public domain is known.
- No backend: the enquiry form opens the visitor's email client or WhatsApp with prefilled content. It does not deliver mail by itself, collect files, or store data. The visitor must send the message and attach drawings themselves. Confirm the phone number is WhatsApp-enabled.

## Before public launch
All equipment illustrations are original simplified procedural 3D concepts, **not photographs of actual Unity Engineering equipment, certified engineering models, fabrication drawings, or AI/stock images**. Some related equipment variants use similar geometry. Replace with approved factory/product photographs or verified CAD-derived renders for a production-grade catalogue. Product descriptions are generic; verify the equipment list, process descriptions, design details, materials and certifications with Unity Engineering before publishing. No unconfirmed certifications, pressure ratings, machinery inventory, production counts, or client logos are asserted. Confirm public use of contact information and the owner name.

## Editing
`build.py` contains the 45-entry catalogue, descriptions, and HTML templates. Run `python build.py` to rebuild the pages; the included pages are already built. `assets/style.css` contains the design system, `assets/engine.js` the procedural 3D geometry/shaders, `assets/app.js` the interactions, and `assets/products/` the rendered thumbnails. `assets/turntable/` contains fallback images. If adding a new model, generate its thumbnail and adjust the catalogue.

No account was created and no public deployment was performed. Live deployment requires the account owner's action or access.
