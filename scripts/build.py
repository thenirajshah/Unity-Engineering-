"""Build the complete static Unity Engineering website."""
from html import escape as e
from hashlib import sha256
from pathlib import Path
from urllib.parse import quote, urlsplit
import json
import os
import shutil

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
DIST = Path('dist')
ASSET_VERSION = {
    suffix: sha256(Path(f'public/assets/site.{suffix}').read_bytes()).hexdigest()[:10]
    for suffix in ('css', 'js')
}
PRODUCTS = json.loads(Path('src/products.json').read_text())
CATEGORIES = json.loads(Path('src/categories.json').read_text())
PAGES = json.loads(Path('src/pages.json').read_text())
COMPONENTS = json.loads(Path('src/components.json').read_text())
FEATURED = ['reactor-limpet', 'exchanger', 'pressure', 'anfd', 'ribbon']
SHOWCASE = ['reactor-limpet', 'exchanger', 'anfd']
INDUSTRIES = json.loads(Path('src/industries.json').read_text())
LEGACY_CATEGORY = '/products/categories/heat-exchangers-columns/'
EMAIL = 'Nirajkumarshah17@gmail.com'
PHONE = '+91 9934969351'
ADDRESS = 'Plot No. 5122, 4th S Rd, Ankleshwar GIDC, Ankleshwar, Gujarat 393002, India'
MAP = 'https://www.google.com/maps/search/?api=1&query=' + quote(ADDRESS)
SITE = os.environ.get('SITE_URL', '').rstrip('/')
if not SITE and os.environ.get('CF_PAGES') == '1' and os.environ.get('CF_PAGES_BRANCH') == 'main':
    SITE = 'https://unity-engineering.pages.dev'
if SITE:
    parsed = urlsplit(SITE)
    if parsed.scheme != 'https' or not parsed.netloc or parsed.path or parsed.query or parsed.fragment:
        raise ValueError('SITE_URL must be an HTTPS origin')
assert len(CATEGORIES) == 6 and len(PRODUCTS) == 23
assert len({p['slug'] for p in PRODUCTS}) == len({p['kind'] for p in PRODUCTS}) == 23
assert {p['cat'] for p in PRODUCTS} == set(range(6))

def url(p):
    return '/products/' + p['slug'] + '/'

def caturl(i):
    return '/products/categories/' + CATEGORIES[i][0] + '/'

def quoteurl(p):
    return '/quotation/?equipment=' + quote(p['slug'])

def whatsapp(p):
    return 'https://wa.me/919934969351?text=' + quote(
        f'Hello Unity Engineering, I would like to enquire about {p["title"]}.'
    )

def image(p):
    approval = p.get('approved_image')
    if approval:
        asset = approval['asset']
        root = Path('public/assets/equipment').resolve()
        path = (Path('public/assets') / asset).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f'Invalid approved image for {p["slug"]}')
        return '/assets/equipment/' + quote(path.relative_to(root).as_posix())
    return ''

def pic(p, style='', eager=False, variant='primary',
        sizes='(max-width: 700px) 90vw, (max-width: 1024px) 45vw, 36vw'):
    asset = image(p)
    if not asset:
        return f'<div class="image-pending {style}">Image pending</div>'
    approval = p['approved_image']
    width, height = approval['width'], approval['height']
    source_set = ''
    if variant in approval:
        asset = '/assets/' + approval[variant]['asset']
        width, height = approval[variant]['width'], approval[variant]['height']
    elif 'small' in approval:
        source_set = (
            f' srcset="/assets/{e(approval["small"])} {approval["small_width"]}w, {e(asset)} {approval["width"]}w"'
            f' sizes="{sizes}"'
        )
    priority = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return f'<img class="{style}" src="{e(asset)}"{source_set} alt="{e(approval["label"])} of {e(p["title"])}" width="{width}" height="{height}" {priority} decoding="async">'

def image_caption(p):
    approval = p.get('approved_image')
    if not approval:
        return ''
    credit = ''
    if approval.get('source'):
        credit = f' · <a href="{e(approval["source"])}">{e(approval["credit"])}</a> ({e(approval["licence"])})'
    return e(approval['label']) + credit

def industry_cards(heading='h3'):
    by_slug = {c[0]: i for i, c in enumerate(CATEGORIES)}
    return '<div class="industry-grid">' + ''.join(
        f'<article><span class="industry-mark" aria-hidden="true"></span><{heading}>{e(title)}</{heading}><p>{e(description)}</p><div class="industry-links">'
        + links([(caturl(by_slug[key]), e(CATEGORIES[by_slug[key]][1])) for key in related], '')
        + '</div></article>' for _,title,description,related in INDUSTRIES
    ) + '</div>'

def brand():
    return '<a href="/" class="brand" aria-label="Unity Engineering home"><img src="/assets/v3/logo-nav.webp" alt="" width="36" height="40"><span>UNITY<strong>ENGINEERING</strong></span></a>'

def button(path, label, style=''):
    download = ' download' if path.endswith('.pdf') else ''
    return f'<a class="btn {style}" href="{e(path)}"{download}>{e(label)}</a>'

def links(entries, path):
    return ''.join(f'<a href="{href}"' + (' aria-current="page"' if path == href else '') + f'>{label}</a>' for href, label in entries)

def header(path):
    mega = ''.join(
        f'<div><a class="menu-cat" href="{caturl(i)}">{e(c[1])}</a>'
        + links([(url(p), e(p['title'])) for p in PRODUCTS if p['cat'] == i], path) + '</div>'
        for i, c in enumerate(CATEGORIES)
    )
    current = ' class="active"' if path.startswith('/products/') or path == '/equipment-lookbook/' else ''
    return f'''<a class="skip" href="#main">Skip to content</a><header class="header" id="top">
<div class="nav shell">{brand()}<button type="button" class="menu-button" aria-expanded="false" aria-controls="navigation">Menu</button>
<nav id="navigation" aria-label="Primary navigation">{links([("/", "Home"), ("/about/", "About")],path)}
<details class="mega"><summary{current}>Products</summary><div class="mega-panel"><div class="shell"><div class="mega-lead"><a class="menu-cat" href="/products/">Browse full catalogue <span class="arrow-up" aria-hidden="true"></span></a>{links([('/equipment-lookbook/', 'Equipment lookbook')], path)}<a href="/catalogue/">Download PDF</a></div><div class="mega-grid">{mega}</div></div></div></details>
{links([("/manufacturing/","Manufacturing"),("/industries/","Industries"),("/gallery/","Gallery"),("/contact/","Contact")], path)}
<a class="drawer-quote" href="/quotation/">Request a Quote</a></nav>
{button('/quotation/', 'Request a Quote', 'nav-quote')}</div></header>'''

def footer():
    sitemap = links([('/about/','About'),('/manufacturing/','Manufacturing'),('/engineering/','Engineering capabilities'),('/infrastructure/','Infrastructure'),('/quality/','Quality Assurance'),('/industries/','Industries'),('/gallery/','Gallery'),('/privacy/','Privacy Policy')], '')
    return f'''<footer class="footer"><div class="shell footer-grid"><div>{brand()}<p>Precision Fabrication.<br>Engineered for Performance.</p></div>
<div><h2>Company</h2>{sitemap}</div><div><h2>Equipment</h2>{links([(caturl(i),e(c[1])) for i,c in enumerate(CATEGORIES)], '')}<a href="/catalogue/">PDF catalogue</a></div>
<div><h2>Contact</h2><address>{ADDRESS}</address><a href="tel:+919934969351">{PHONE}</a><a href="mailto:{EMAIL}">{EMAIL}</a></div></div>
<div class="shell footer-end"><span>© Unity Engineering</span><a href="#top">Back to top</a></div></footer>'''

def page(path, title, summary, content, trail=(), structured=None):
    label = title + ' | Unity Engineering' if path != '/' else title
    schema = [{"@context":"https://schema.org", "@type":"Organization", "name":"Unity Engineering",
               "foundingDate":"2006", "telephone":"+919934969351", "email":EMAIL,
               "address":{"@type":"PostalAddress","streetAddress":"Plot No. 5122, 4th S Rd, Ankleshwar GIDC","addressLocality":"Ankleshwar","addressRegion":"Gujarat","postalCode":"393002","addressCountry":"IN"}}]
    if SITE:
        schema[0].update(url=SITE, logo=SITE+'/assets/logo.png')
    if trail and SITE:
        schema.append({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
            {"@type":"ListItem", "position":i, "name":name, "item":SITE+href}
            for i,(href,name) in enumerate([('/','Home'),*trail,(path,title)],1)]})
    if structured:
        schema.append(structured)
    canonical = f'<link rel="canonical" href="{e(SITE+path)}"><meta property="og:url" content="{e(SITE+path)}">' if SITE else '<meta name="robots" content="noindex">'
    if path == '/404.html':
        canonical = '<meta name="robots" content="noindex">'
    social = SITE + (structured['image'].removeprefix(SITE) if structured and structured.get('image') else '/assets/v3/social.webp')
    page_type = 'home' if path == '/' else ('catalogue-page' if path == '/products/' else 'inner')
    if structured:
        page_type += ' product-page'
    bread = ''
    if path not in ('/', '/404.html'):
        bread = f'<nav class="shell breadcrumb" aria-label="Breadcrumb">{links([("/", "Home"), *((href,e(name)) for href,name in trail)], "")}<span aria-current="page">{e(title)}</span></nav>'
    preload = '<link rel="preload" as="image" href="/assets/v3/reactor-mobile.webp" media="(max-width: 700px)" fetchpriority="high">' if path == '/' else ''
    document = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(label)}</title><meta name="description" content="{e(summary)}">
<meta property="og:title" content="{e(label)}"><meta property="og:description" content="{e(summary)}"><meta property="og:type" content="website">
<meta property="og:site_name" content="Unity Engineering"><meta property="og:locale" content="en_IN">
<meta property="og:image" content="{e(social)}"><meta name="twitter:card" content="summary_large_image">{canonical}
{preload}<link rel="icon" href="/assets/favicon.png"><link rel="stylesheet" href="/assets/site.css?v={ASSET_VERSION['css']}">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace('<',chr(92)+'u003c')}</script><script src="/assets/site.js?v={ASSET_VERSION['js']}" defer></script>
</head><body class="{page_type}">{header(path)}<main id="main" tabindex="-1">{bread}{content}</main>{footer()}</body></html>'''
    out = DIST / path.strip('/')
    if path.endswith('/'):
        out = out / 'index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(document)

def intro(label, heading, description, style=''):
    return f'<section class="shell intro {style}"><p class="kicker">{e(label)}</p><h1>{e(heading)}</h1><p class="lede">{e(description)}</p></section>'

def section(label, heading, content, style='', action=''):
    return f'<section class="band {style}"><div class="shell"><div class="section-head" data-reveal><div><p class="kicker">{e(label)}</p><h2>{e(heading)}</h2></div>{action}</div>{content}</div></section>'

def card(p, preview=False, large=False):
    search = e(' '.join([p['title'],p['desc'],p['kind'],CATEGORIES[p['cat']][1]]), quote=True)
    quick = (f'<button class="link preview" type="button" data-image="{e(image(p))}" data-title="{e(p["title"])}" data-detail="{e(p["desc"])}" hidden>Quick preview</button>' if preview else '')
    heading = 'h2' if preview else 'h3'
    photo = pic(p, sizes='(max-width: 700px) 92vw, (max-width: 1712px) 45vw, 764px') if large else pic(p, variant='card')
    return f'''<article class="card" data-category="{p["cat"]}" data-search="{search}">
<a class="card-image" href="{url(p)}" tabindex="-1" aria-hidden="true">{photo}</a>
<div class="card-body"><p class="kicker">{e(CATEGORIES[p["cat"]][1])}</p><{heading}><a href="{url(p)}">{e(p["title"])}</a></{heading}>
<p>{e(p["desc"])}</p>
<div class="card-actions"><a href="{url(p)}">View details <span class="arrow-up" aria-hidden="true"></span></a>{quick}<a href="{quoteurl(p)}">Request quotation</a></div></div></article>'''

def cards(products, preview=False, large=False):
    style = 'cards large-photos' if large else 'cards'
    return f'<div class="{style}">' + ''.join(card(p, preview, large) for p in products) + '</div>'

def viewer(p, hero=False):
    fallback = '' if hero else pic(p, 'viewer-still')
    mode = ' hero-viewer' if hero else ''
    cutaway = '<button type="button" data-control="cutaway" aria-pressed="false">Tube bundle</button><button type="button" data-control="exploded" aria-pressed="false">Exploded assembly</button>' if p['kind'] == 'exchanger' else ''
    components = '' if hero else '<div class="components" hidden aria-label="Equipment components">' + ''.join(
        f'<button class="btn outline" type="button" data-component data-yaw="{yaw}" data-pitch="{pitch}" data-note="{e(note)}" aria-pressed="false">{e(label)}</button>'
        for label,note,yaw,pitch in COMPONENTS[p['kind']]) + '</div><p class="component-note" role="status"></p>'
    return f'''<div class="viewer{mode}" data-viewer data-kind="{p["kind"]}" data-hero="{str(hero).lower()}">
{fallback}<canvas tabindex="0" aria-label="Interactive equipment model. Use arrow keys to rotate and plus or minus to zoom." hidden></canvas>
<div class="viewer-tools"><button class="btn launch" type="button" hidden>Launch interactive 3D</button>
<div class="viewer-controls" hidden><button type="button" data-control="rotate" aria-pressed="false">Auto-rotate</button><button type="button" data-control="in" aria-label="Zoom in">+</button><button type="button" data-control="out" aria-label="Zoom out">−</button><button type="button" data-control="reset">Reset</button><button type="button" data-control="fullscreen">Fullscreen</button>{cutaway}</div>
<p class="viewer-status" role="status"></p></div></div>{components}'''

def category_cards():
    return '<div class="category-grid">' + ''.join(
        f'<a class="category" href="{caturl(i)}">'
        f'{pic(next(p for p in PRODUCTS if p["cat"] == i), variant="thumb")}<div><h3>{e(c[1])}</h3><p>{e(c[2])}</p></div><span class="arrow-up category-arrow" aria-hidden="true"></span></a>'
        for i,c in enumerate(CATEGORIES)) + '</div>'

def product_gallery(p):
    caption = image_caption(p)
    primary = image(p)
    variants = [('Full equipment', primary)]
    if p['approved_image'].get('detail'):
        variants.append(('Component detail', '/assets/' + p['approved_image']['detail']))
    thumbs = ''
    if len(variants) > 1:
        thumbs = '<div class="gallery-controls" aria-label="Equipment views" hidden>' + ''.join(
            f'<button type="button" data-gallery-src="{e(path)}" aria-pressed="{str(i == 0).lower()}">{e(label)}</button>'
            for i, (label, path) in enumerate(variants)
        ) + '</div>'
    return f'''<figure class="product-image" data-product-gallery>
<a class="product-image-link" href="{e(primary)}" aria-label="Zoom equipment image">{pic(p, eager=True)}<span aria-hidden="true">+</span></a>
{thumbs}
<dialog class="image-dialog" aria-label="Equipment image"><form method="dialog"><button class="btn outline" type="submit">Close image</button></form>
<img width="{p['approved_image']['width']}" height="{p['approved_image']['height']}" alt="" hidden></dialog><figcaption>{caption}</figcaption></figure>'''

def contact_block():
    return f'''<div class="contact-cols"><div><h3>Visit</h3><address>{ADDRESS}</address>{button(MAP, "Open in Maps", "outline")}</div>
<div><h3>Call or message</h3><p>{PHONE}</p><div class="actions">{button("tel:+919934969351", "Call", "outline")}{button("https://wa.me/919934969351", "WhatsApp", "outline")}</div></div>
<div><h3>Email</h3><p>{EMAIL}</p>{button(f"mailto:{EMAIL}", "Send email", "outline")}</div></div>'''

def quote_banner():
    return f'<div class="quote-band"><p class="kicker">Project enquiries</p><h2>Discuss your equipment requirements.</h2>{button("/quotation/","Request a Quotation")}</div>'

def process_sequence(stages):
    return '<ol class="timeline">' + ''.join(
        f'<li data-reveal><div><h3>{e(title)}</h3><p>{e(description)}</p></div></li>'
        for title, description in stages
    ) + '</ol>'

def build_home():
    hero_product = next(p for p in PRODUCTS if p['kind'] == 'reactor-limpet')
    hero = f'''<section class="hero">
<picture class="hero-art"><source media="(max-width: 700px)" srcset="/assets/v3/reactor-mobile.webp"><img src="/assets/v3/reactor-hero.webp" srcset="/assets/v3/reactor-1080.webp 1080w, /assets/v3/reactor-hero.webp 1536w" sizes="(min-width: 1550px) 1162px, (min-width: 1140px) 75vw, 855px" width="1536" height="1024" alt="Concept visualization of a stainless steel limpet coil reactor with an external half-pipe coil" fetchpriority="high"></picture>
<div class="shell hero-layout"><div class="hero-copy"><p class="kicker hero-kicker">Process equipment fabrication</p>
<h1>Engineered for<br>precision.<br><em>Built for industry.</em></h1>
<p class="lede">Custom process equipment for pharmaceutical, chemical and industrial applications, fabricated in Ankleshwar, Gujarat.</p>
<div class="actions">{button('/products/', 'Explore equipment')}<a class="hero-enquiry" href="/quotation/">Discuss your project <span class="arrow-up" aria-hidden="true"></span></a></div></div>
<div class="hero-visual">{viewer(hero_product, True)}<div class="hero-caption"><span>Limpet coil reactor</span><small>Concept visualization</small></div></div></div></section>
<div class="hero-facts"><div class="shell statbar"><div><b>2006</b><span>Established</span></div><div><b>{len(PRODUCTS)}</b><span>Equipment entries</span></div><div class="stat-location"><span>Fabrication location</span>ANKLESHWAR GIDC, GUJARAT</div></div></div>'''
    about = f'''<div class="shell home-intro" data-reveal><div><p class="kicker">Unity Engineering</p><h2>Built around your process.</h2></div><div><p class="lede">We fabricate equipment for reaction, heat transfer, separation and batch processing. Operating conditions, materials and plant interfaces guide the configuration from the first enquiry.</p>{button('/about/', 'About Unity Engineering', 'outline')}</div></div>'''
    body = hero + '<section class="light intro-band">'+about+'</section>'
    body += section('Equipment catalogue','Find equipment by process duty.',category_cards(), 'light equipment-band', button('/products/','View all equipment','outline'))
    selected = [next(p for p in PRODUCTS if p['kind'] == kind) for kind in SHOWCASE]
    body += section('Featured equipment','Explore key configurations.',cards(selected), 'light feature-band', button('/equipment-lookbook/', 'Open equipment lookbook', 'outline'))
    body += section('Industries We Serve','Solutions for Critical Manufacturing Environments',industry_cards(),'industries-band',button('/industries/','View industries','outline'))
    stages = [
        ('Define the duty','Agree operating conditions, product contact materials and plant interfaces.'),
        ('Plan the fabrication','Review drawing requirements, forming, welding and assembly for the project.'),
        ('Agree acceptance','Define inspection, testing and handover requirements before fabrication.'),
    ]
    process = f'''<div class="story process-story">
<figure><img src="/assets/fabrication/welding.webp" alt="Concept visualization of metal components being welded" width="392" height="392" loading="lazy"><figcaption>Weld preparation and assembly · Concept visualization</figcaption></figure>
<div>{process_sequence(stages)}{button('/engineering/','Explore engineering capabilities','outline')}</div></div>'''
    body += section('Manufacturing','From design basis to dispatch.',process,'light process-band',button('/manufacturing/','See fabrication workflow','outline'))
    proof = f'''<div class="story proof-story"><div><p class="kicker">Quality assurance</p><h2>Acceptance begins with the specification.</h2><p class="lede">Agree the checks that matter to your equipment, from dimensional fit to finish, testing and handover records.</p>{button('/quality/','Explore the quality approach','outline')}</div>
<figure><img src="/assets/v3/inspection.webp" alt="Concept visualization of a machined stainless steel tube sheet under inspection" width="1050" height="700" loading="lazy"><figcaption>Tube sheet inspection · Concept visualization</figcaption></figure></div>'''
    body += f'<section class="band assurance-band"><div class="shell">{proof}</div></section>'
    body += section('Gallery','A closer look at the equipment.',cards([selected[1],selected[2]]),'light gallery-feature',button('/gallery/','Open equipment gallery','outline'))
    body += '<section class="band light"><div class="shell">'+quote_banner()+contact_block()+'</div></section>'
    page('/', 'Unity Engineering | Process Equipment Fabricator in Ankleshwar', f'Pharmaceutical, chemical and industrial process equipment fabrication in Ankleshwar, Gujarat. Explore {len(PRODUCTS)} equipment entries and request a quotation.', body)

def build_lookbook():
    by_kind = {p['kind']: p for p in PRODUCTS}
    selection = [by_kind[k] for k in ('reactor-limpet', 'exchanger', 'column', 'pressure', 'anfd', 'ribbon')]
    details = []
    index = []
    sizes = '(max-width: 540px) 91vw, (max-width: 820px) 57vw, (max-width: 1714px) 36vw, 614px'
    for i, p in enumerate(selection):
        title = e(p['title'])
        category = e(CATEGORIES[p['cat']][1])
        details.append(f'''<article class="lineup-detail" id="look-{e(p['kind'])}">
<div class="lineup-photo">{pic(p, eager=i == 0, sizes=sizes)}<span class="lineup-credit">{image_caption(p)}</span></div>
<div class="lineup-copy"><p class="kicker">{category}</p><h2>{title}</h2>
<p class="lineup-description">{e(p['desc'])}</p><dl>
<div><dt>Application</dt><dd>{e(p['application'])}</dd></div>
<div><dt>Construction features</dt><dd>{e(p['features'])}</dd></div></dl>
<div class="actions">{button(quoteurl(p), 'Request quotation')}{button(url(p), 'View equipment', 'outline')}</div></div></article>''')
        index.append(f'<a href="#look-{e(p["kind"])}">{category}</a>')
    content = f'''<link rel="stylesheet" href="/assets/lineup.css"><script defer src="/assets/lineup.js"></script>
<section class="shell lineup" aria-labelledby="lookbook-title">
<div class="lineup-heading"><h1 id="lookbook-title">Equipment lookbook</h1><a href="/products/">Full catalogue <i class="arrow-up" aria-hidden="true"></i></a></div>
<div class="lineup-layout"><figure class="lineup-exhibit" hidden>
<div class="lineup-stage" tabindex="0" role="group" aria-label="Equipment photographs. Use left and right arrow keys to browse."></div>
<figcaption class="lineup-tools"><span class="lineup-credits"></span>
<div class="lineup-controls"><span class="lineup-count" role="status" aria-atomic="true">
<b>01</b> / {len(selection):02d}<span class="lineup-sr"></span></span>
<button type="button" data-step="-1" aria-label="Previous equipment"><i aria-hidden="true"></i></button>
<button type="button" data-step="1" aria-label="Next equipment"><i aria-hidden="true"></i></button></div></figcaption>
</figure><div class="lineup-details">{''.join(details)}</div></div>
<nav class="lineup-index" aria-label="Select equipment by category">{''.join(index)}</nav></section>'''
    page('/equipment-lookbook/', 'Equipment Lookbook', 'Explore six process equipment configurations and their applications, construction features and quotation options.', content, [('/products/', 'Products')])

def build_products():
    choices = ''.join(f'<option value="{i}">{e(c[1])}</option>' for i,c in enumerate(CATEGORIES))
    filters = f'''<div class="catalog-controls">
<label for="search">Search equipment<input id="search" type="search" placeholder="e.g. limpet, vacuum dryer"></label>
<label for="category">Category<select id="category"><option value="">All categories</option>{choices}</select></label>
<button type="button" class="btn outline" id="clear-filters" disabled>Clear filters</button></div>
<div class="catalog-status"><p id="count" role="status">{len(PRODUCTS)} equipment entries</p><a href="/assets/catalogue.pdf" download>Download PDF catalogue</a></div>'''
    dialog = '<dialog id="preview-dialog" aria-labelledby="preview-title"><form method="dialog"><button class="link" aria-label="Close quick preview">Close</button></form><img width="640" height="540" alt="" hidden><div class="image-pending">Image pending</div><h2 id="preview-title"></h2><p></p><div class="actions"><a class="btn detail-link">View details</a><a class="btn outline quote-link">Request quotation</a></div></dialog>'
    page('/products/', 'Process Equipment Catalogue', 'Find reactors, heat exchangers, vessels, dryers and mixers for process equipment fabrication in Ankleshwar, Gujarat.', intro('Process equipment','Find your equipment.',f'Filter {len(PRODUCTS)} configurations by process duty or equipment name.', 'compact-intro')+'<section class="shell catalog">'+filters+f'<p id="no-results" hidden>No equipment matches your search.</p><div id="product-grid">{cards(PRODUCTS, preview=True, large=True)}</div>'+dialog+'</section>'+section('Equipment families','Explore by category.',category_cards(),'light'))
    for i,(_,title,description) in enumerate(CATEGORIES):
        products = [p for p in PRODUCTS if p['cat'] == i]
        banner = pic(products[0])
        page(caturl(i),title,description, '<div class="shell category-hero">'+intro('Equipment category',title,description)+banner+'</div>'+section('Category equipment','Browse equipment.',cards(products, large=True), 'light'), [('/products/','Products')])
    for p in PRODUCTS:
        title = p['title']
        gallery = product_gallery(p)
        tech = f'''<div class="detail-grid"><div class="engineering-copy"><h3>Working principle</h3><p>{e(p['principle'])}</p><h3>Industrial applications</h3><p>{e(p['application'])}</p><h3>Construction features</h3><p>{e(p['features'])}.</p></div>
<div class="spec-panel"><h3>Technical specifications</h3><dl class="tech spec-rows">
<div><dt>Configuration</dt><dd>Application-specific geometry and process interfaces</dd></div>
<div><dt>Design pressure and temperature</dt><dd>As applicable to the duty</dd></div>
<div><dt>Material options</dt><dd>Product-contact and structural grades selected for compatibility and approved engineering specifications</dd></div>
<div><dt>Customization</dt><dd>Access, support and connection arrangements subject to project requirements</dd></div>
<div><dt>Inspection and acceptance</dt><dd>As per the agreed project scope</dd></div></dl><a href="/engineering/">Explore the engineering basis</a></div></div>'''
        has_3d = p['kind'] in FEATURED
        viz = '<div id="interactive-model">'+section('Interactive equipment','Inspect the concept model.',viewer(p)+'<p class="caption">Illustrative geometry · Final construction is project-specific.</p>')+'</div>' if has_3d else ''
        related = [other for other in PRODUCTS if other is not p and other['cat'] == p['cat']][:3]
        product_quote = button(quoteurl(p),'Request quotation for this equipment') + button(whatsapp(p), 'Enquire on WhatsApp', 'outline')
        detail_links = [('#engineering','Engineering details')]
        if has_3d:
            detail_links.append(('#interactive-model','Interactive 3D'))
        lead = f'''<section class="shell product-hero"><div>
<p class="kicker">{e(CATEGORIES[p['cat']][1])}</p><h1>{e(title)}</h1><p class="lede">{e(p['desc'])}</p>
<p class="product-application">{e(p['application'])}</p><div class="actions">{product_quote}</div>
<nav class="product-nav" aria-label="Product sections">{links(detail_links,'')}</nav></div>{gallery}</section>'''
        content = lead+'<div id="engineering">'+section('Engineering overview','Process and construction.',tech,'light')+'</div>'+viz+(section('Related equipment','Explore related configurations.',cards(related),'light') if related else '')
        schema = {'@context':'https://schema.org','@type':'Product','name':title,'description':p['desc'],'category':CATEGORIES[p['cat']][1]}
        if image(p):
            schema['image'] = SITE + image(p)
        page(url(p),title,p['desc']+' Discuss your process equipment fabrication requirements with Unity Engineering in Ankleshwar.',content,[('/products/','Products'),(caturl(p['cat']),CATEGORIES[p['cat']][1])],schema)
        # Keep inbound links to V1 product URLs working.
        legacy = DIST / 'products' / (p['slug']+'.html')
        if not SITE:
            legacy.write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url={url(p)}"><title>{e(title)}</title><a href="{url(p)}">Open {e(title)}</a></html>')

def build_information():
    page(LEGACY_CATEGORY, 'Heat Exchangers & Columns', 'Find heat exchangers and columns in their dedicated categories.',
         intro('Equipment categories', 'Heat Exchangers & Columns', 'Browse either equipment category.')
         +'<div class="shell actions">'+button(caturl(1),'Heat Exchangers')+button(caturl(2),'Columns')+'</div>',
         [('/products/','Products')])
    page('/industries/', 'Industries We Serve', 'Process equipment applications for pharmaceuticals, agrochemicals, fine and specialty chemicals, and process R&D.',
         intro('Industries We Serve', 'Solutions for Critical Manufacturing Environments', 'Explore equipment by application.')
         +'<section class="shell industries-page">'+industry_cards('h2')+'</section><div class="shell">'+quote_banner()+'</div>')
    stages = [
        ('drawings','Engineering and drawing preparation'),('cutting','Marking and plasma cutting'),
        ('rolling','Plate rolling'),('forming','Dish end forming'),('coil','Shell, limpet coil and jacket fabrication'),
        ('welding','Nozzle fabrication, fit-up and welding'),('machining','Machining and shaft assembly'),
        ('polishing','Surface finishing, buffing and polishing'),('inspection','Inspection and testing'),
        ('dispatch','Final assembly and dispatch')]
    profiles = {
        'about': ('drawings', 'Reviewing an equipment drawing', 'Equipment built around the project.', '/manufacturing/', 'Explore manufacturing'),
        'manufacturing': ('welding', 'Welding a vessel component', 'Fabrication sequence.', '/engineering/', 'Engineering capabilities'),
        'engineering': ('drawings', 'Reviewing an equipment drawing', 'From duty to approved drawings.', '/quality/', 'See quality approach'),
        'infrastructure': ('dispatch', 'Preparing equipment for dispatch', 'Plan equipment interfaces and delivery.', '/contact/', 'Discuss site requirements'),
        'quality': ('inspection', 'Inspecting a fabricated component', 'Agree the acceptance criteria.', '/quotation/', 'Share your specification'),
    }
    for slug, (label, heading, description, *sections) in PAGES.items():
        if slug == 'industries':
            continue
        if slug == 'privacy':
            content = intro(label,heading,description,'compact-intro')
            content += '<div class="shell legal-copy">'+''.join(f'<section><h2>{e(h)}</h2><p>{e(t)}</p></section>' for h,t in sections)+'</div>'
            page('/privacy/',label,description,content)
            continue
        visual, image_description, subject, action_path, action_label = profiles[slug]
        photo, width, height = (('/assets/v3/inspection.webp', 1050, 700) if slug == 'quality' else (f'/assets/fabrication/{visual}.webp', 392, 392))
        content = f'''<div class="shell editorial-hero">{intro(label,heading,description)}
<figure><img src="{photo}" alt="Concept depiction of {e(image_description.lower())}" width="{width}" height="{height}">
<figcaption>{e(image_description)} · Concept visualization</figcaption></figure></div>'''
        overview = process_sequence(sections) if slug in ('manufacturing', 'engineering') else '<div class="process-list">'+''.join(f'<article data-reveal><h3>{e(h)}</h3><p>{e(t)}</p></article>' for h,t in sections)+'</div>'
        content += section(label,subject,overview,'light',button(action_path,action_label,'outline'))
        if slug == 'manufacturing':
            content += section('Fabrication workflow','Stages from preparation to dispatch.', '<p class="lede">An illustrative fabrication sequence. The approved project scope determines which stages and facilities are required.</p><div class="image-grid process-grid">'+''.join(f'<figure data-reveal><img src="/assets/fabrication/{key}.webp" alt="Concept depiction of {e(stage.lower())}" width="392" height="392" loading="lazy"><figcaption>{e(stage)}</figcaption></figure>' for key,stage in stages)+'</div>')
        if slug in ('infrastructure','about'):
            content += section('Contact','Find Unity Engineering.',contact_block())
        page('/'+slug+'/',label,description,content+'<div class="shell">'+quote_banner()+'</div>')
    contact_intro = intro('Contact','Talk to Unity Engineering.','Tell us about your process requirements and project timeline.','compact-intro')
    page('/contact/','Contact Us','Contact Unity Engineering in Ankleshwar, Gujarat for process equipment fabrication enquiries.',contact_intro+section('Ankleshwar, Gujarat','Contact the workshop.',contact_block(),'light',button('/quotation/','Start an equipment enquiry')))
    gallery_nav = '<nav class="shell gallery-nav" aria-label="Gallery categories">'+links([('#'+c[0],e(c[1])) for c in CATEGORIES],'')+'</nav>'
    galleries = []
    for i,(slug,title,_) in enumerate(CATEGORIES):
        images = ''.join(
            f'<figure><a href="{url(p)}">{pic(p)}</a><figcaption><a href="{url(p)}">{e(p["title"])}</a><span>{image_caption(p)}</span></figcaption></figure>'
            for p in PRODUCTS if p['cat']==i
        )
        galleries.append(f'<div id="{slug}">'+section('Equipment gallery',title,'<div class="image-grid gallery-grid">'+images+'</div>')+'</div>')
    page('/gallery/','Equipment Gallery','Equipment images by product family from Unity Engineering.',intro('Gallery','Equipment in detail.','Browse concept renders by equipment family and open a product to explore its design and applications.','compact-intro')+gallery_nav+''.join(galleries))
    pdf_intro = intro('Product catalogue','Download the equipment catalogue.',f'A PDF guide with a full page and equipment illustration for each of our {len(PRODUCTS)} products.','compact-intro')
    pdf_actions = '<div class="shell actions catalogue-download">'+button('/assets/catalogue.pdf','Download equipment catalogue PDF')+button('/products/','Browse products online','outline')+'</div>'
    page('/catalogue/','Download Product Catalogue','Download the Unity Engineering process equipment catalogue PDF.',pdf_intro+pdf_actions+section('Equipment families','Browse the online catalogue.',category_cards(),'light'))
    fields = [
        ('name','Customer name','text','name',True),('company','Company name','text','organization',True),
        ('email','Email','email','email',True),('phone','Mobile number','tel','tel',True),
        ('material','Material requirement','text','off',False),
        ('pressure','Design pressure','text','off',False),('temperature','Design temperature','text','off',False)]
    inputs = [f'<label for="{key}">{label}<input id="{key}" name="{key}" type="{kind}" autocomplete="{auto}" maxlength="150"{" required" if required else ""}></label>' for key,label,kind,auto,required in fields]
    cats = ''.join(f'<option value="{i}">{e(c[1])}</option>' for i,c in enumerate(CATEGORIES))
    options = ''.join(
        f'<option value="{p["slug"]}" data-category="{p["cat"]}">{e(p["title"])}</option>'
        for p in PRODUCTS
    )
    enquiry = f'''<form id="enquiry" action="/contact/" class="enquiry">
<fieldset><legend>Contact details</legend><div class="form-grid">{''.join(inputs[:4])}</div></fieldset>
<fieldset><legend>Equipment</legend><div class="form-grid">
<label for="equipment-category">Equipment category<select id="equipment-category" name="category"><option value="">Select a category</option>{cats}</select></label>
<label for="equipment-name">Equipment name<select id="equipment-name" name="equipment"><option value="">Select equipment</option>{options}</select></label>
</div></fieldset>
<fieldset><legend>Project requirements</legend><div class="form-grid">{''.join(inputs[4:])}
<label class="wide" for="requirements">Process and project details<textarea id="requirements" name="requirements" rows="5" maxlength="1500" required></textarea></label></div></fieldset>
<div class="actions"><button class="btn" type="submit" value="email" disabled>Open email draft</button><button class="btn outline" type="submit" value="whatsapp" disabled>Open WhatsApp draft</button></div><p role="status" id="form-status"></p>
<noscript><p>Use the direct email or phone links to share your enquiry.</p></noscript></form>'''
    page('/quotation/','Request a Quotation','Prepare a project enquiry for Unity Engineering and send it through your email app or WhatsApp.', intro('Project enquiry','Request a quotation.','Prepare a draft with your process requirements and send it in your email or WhatsApp app.','compact-intro')+section('Equipment enquiry','Tell us about the project.',enquiry,'light')+section('Direct enquiry','Contact Unity Engineering.',contact_block()))
    page('/404.html','Page not found','Explore the Unity Engineering equipment catalogue or return to the homepage.',intro('Error 404','This page has moved or is unavailable.','Find equipment by category or return to the Unity Engineering homepage.')+'<div class="shell actions catalogue-download">'+button('/','Back to home')+button('/products/','Browse equipment','outline')+'</div>'+section('Equipment families','Find the equipment you need.',category_cards(),'light'))

if DIST.exists():
    shutil.rmtree(DIST)
shutil.copytree('public', DIST)
for folder in ('renders', 'products', 'categories', 'details'):
    shutil.rmtree(DIST/'assets'/folder, ignore_errors=True)
(DIST/'assets/models/rmg.glb').unlink(missing_ok=True)
shutil.copyfile('src/engine.js', DIST/'assets/engine.js')
build_home()
build_lookbook()
build_products()
build_information()
paths = sorted('/' if p.parent == DIST else '/'+p.parent.relative_to(DIST).as_posix()+'/' for p in DIST.rglob('index.html'))
redirects = [f'/products/{p["slug"]}.html {url(p)} 301' for p in PRODUCTS]
redirects.extend(f'{old} {new} 301' for old,new in json.loads(Path('src/redirects.json').read_text()).items())
(DIST/'_redirects').write_text('\n'.join(redirects)+'\n')
if SITE:
    (DIST/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
    (DIST/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{e(SITE+path)}</loc></url>' for path in paths)+'</urlset>')
else:
    (DIST/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
print(f'Built {len(paths)} routes plus custom 404 ({len(PRODUCTS)} equipment, {len(CATEGORIES)} categories)')
