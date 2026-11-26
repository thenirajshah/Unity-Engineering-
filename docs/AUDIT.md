# Source and design audit

The supplied Version 1 archive is preserved in Git at `v1.0.0`. It contained a Python page generator, a long static homepage, 45 linked product pages, a complete catalogue dataset, a user-supplied orange mark, compact procedural renders, a custom WebGL engine and six frame-based fallbacks. Its documentation described manual Cloudflare deployment and did not identify a production project.

V1 used a page-length multi-section navigation model and offered no dedicated category pages, downloadable catalogue, stable single equipment source for editorial data, or automated checks. The viewer initialized eagerly wherever embedded and its unsupported-WebGL mode preloaded complete frame sets. Canonicals and sitemap depended on manual configuration. V2 preserves the catalogue scope, original logo, existing detail slugs and enquiry channels and adds dedicated routes, crawlable navigation, on-demand models, original concept imagery and domain-gated indexing.

## Industry references

- HLE Glascoat and De Dietrich organize equipment by treatment process and show applications close to enquiry paths. HLE's supplied reference photos were inspected for scale and framing and are excluded from the build. [HLE Glascoat](https://www.hleglascoat.com/) · [De Dietrich](https://www.ddpsinc.com/)
- Alfa Laval, Büchi and Sulzer were consulted for the relationship between equipment families, industries and engineering context. [Alfa Laval](https://www.alfalaval.com/) · [Büchi](https://www.buchiglas.com/) · [Sulzer](https://www.sulzer.com/)
- CO2ncrete uses large visual storytelling and scannable text. Awwwards' Three.js index was used to survey approaches to interactive equipment presentation. [CO2ncrete](https://www.co2ncrete.in/) · [Awwwards](https://www.awwwards.com/websites/three-js/)

- GMM Pfaudler’s product-line page and GEA’s fluid-bed processor page were reviewed for task-specific equipment descriptions and the distinction between drying, granulation and coating. Their homepages timed out on the initial request. [GMM Pfaudler](https://www.gmmpfaudler.com/product-lines/pfaudler-1) · [GEA](https://www.gea.com/en/products/dryers-particle-processing/fluid-beds/fluid-bed-processors/)

The implementation uses original imagery, copy and interface design.
