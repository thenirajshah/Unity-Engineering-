"""Build the complete static Unity Engineering website."""
from html import escape as e
from pathlib import Path
from urllib.parse import quote, urlsplit
import json
import os
import shutil

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
DIST = Path('dist')
PRODUCTS = json.loads(Path('src/products.json').read_text())
CATEGORIES = json.loads(Path('src/categories.json').read_text())
PAGES = json.loads(Path('src/pages.json').read_text())
COMPONENTS = json.loads(Path('src/components.json').read_text())
FEATURED = ['reactor-limpet', 'exchanger', 'pressure', 'anfd', 'ribbon', 'rmg']
EMAIL = 'Nirajkumarshah17@gmail.com'
PHONE = '+91 9934969351'
ADDRESS = 'Plot No. 5122, 4th S Rd, Ankleshwar GIDC, Ankleshwar, Gujarat 393002, India'
MAP = 'https://www.google.com/maps/search/?api=1&query=' + quote(ADDRESS)
SITE = os.environ.get('SITE_URL', '').rstrip('/')
if SITE:
    parsed = urlsplit(SITE)
    if parsed.scheme != 'https' or not parsed.netloc or parsed.path or parsed.query or parsed.fragment:
        raise ValueError('SITE_URL must be an HTTPS origin')
assert len(CATEGORIES) == 6 and len(PRODUCTS) == 45
assert len({p['slug'] for p in PRODUCTS}) == len({p['kind'] for p in PRODUCTS}) == 45
assert {p['cat'] for p in PRODUCTS} == set(range(6))

def url(p):
    return '/products/' + p['slug'] + '/'

def caturl(i):
    return '/products/categories/' + CATEGORIES[i][0] + '/'

def quoteurl(p):
    return '/quotation/?equipment=' + quote(p['slug'])

def image(p, alt=False):
    file = p['kind'] + ('-alt' if alt else '') + '.webp'
    if (Path('public/assets/renders') / file).exists():
        return '/assets/renders/' + file
    return '/assets/products/' + p['kind'] + '.webp' if not alt else ''

def pic(p):
    return f'<img src="{image(p)}" alt="Concept visualization of {e(p["title"])}" width="640" height="540" loading="lazy" decoding="async">'

def brand():
    return '<a href="/" class="brand" aria-label="Unity Engineering home"><img src="/assets/logo.webp" alt="" width="36" height="40"><span>UNITY<strong>ENGINEERING</strong></span></a>'

def button(path, label, style=''):
    download = ' download' if path.endswith('.pdf') else ''
    return f'<a class="btn {style}" href="{e(path)}"{download}>{e(label)}</a>'

def links(entries, path):
    return ''.join(f'<a href="{href}"' + (' aria-current="page"' if path == href else '') + f'>{label}</a>' for href, label in entries)

def header(path):
    mega = ''.join(
        f'<div><a class="menu-cat" href="{caturl(i)}">{e(c[1])}</a>' +
        ''.join(f'<a href="{url(p)}">{e(p["title"])}</a>' for p in PRODUCTS if p['cat'] == i) +
        '</div>' for i, c in enumerate(CATEGORIES)
    )
    current = ' class="active"' if path.startswith('/products/') else ''
    return f'''<a class="skip" href="#main">Skip to content</a><header class="header" id="top">
<div class="nav shell">{brand()}<button type="button" class="menu-button" aria-expanded="false" aria-controls="navigation">Menu</button>
<nav id="navigation" aria-label="Primary navigation">{links([("/", "Home"), ("/about/", "About")],path)}
<details class="mega"><summary{current}>Products</summary><div class="mega-panel"><a class="menu-cat" href="/products/">Browse full catalogue</a><div class="mega-grid">{mega}</div></div></details>
{links([("/manufacturing/","Manufacturing"),("/industries/","Industries"),("/gallery/","Gallery"),("/contact/","Contact")], path)}</nav>
{button('/quotation/', 'Request a Quote', 'nav-quote')}</div></header>'''

def footer():
    sitemap = links([('/about/','About'),('/manufacturing/','Manufacturing'),('/infrastructure/','Infrastructure'),('/quality/','Quality Assurance'),('/industries/','Industries'),('/gallery/','Gallery'),('/privacy/','Privacy Policy')], '')
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
    social = SITE + (structured['image'].removeprefix(SITE) if structured else '/assets/hero.webp')
    bread = ''
    if path not in ('/', '/404.html'):
        bread = f'<nav class="shell breadcrumb" aria-label="Breadcrumb">{links([("/", "Home"), *((href,e(name)) for href,name in trail)], "")}<span aria-current="page">{e(title)}</span></nav>'
    document = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(label)}</title><meta name="description" content="{e(summary)}">
<meta property="og:title" content="{e(label)}"><meta property="og:description" content="{e(summary)}"><meta property="og:type" content="website">
<meta property="og:image" content="{e(social)}"><meta name="twitter:card" content="summary_large_image">{canonical}
<link rel="icon" href="/assets/favicon.png"><link rel="stylesheet" href="/assets/site.css">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace('<',chr(92)+'u003c')}</script><script src="/assets/site.js" defer></script>
</head><body>{header(path)}<main id="main">{bread}{content}</main>{footer()}</body></html>'''
    out = DIST / path.strip('/')
    if path.endswith('/'):
        out = out / 'index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(document)

def intro(label, heading, description):
    return f'<section class="shell intro"><p class="kicker">{e(label)}</p><h1>{e(heading)}</h1><p class="lede">{e(description)}</p></section>'

def section(label, heading, content, style='', action=''):
    return f'<section class="band {style}"><div class="shell"><div class="section-head"><div><p class="kicker">{e(label)}</p><h2>{e(heading)}</h2></div>{action}</div>{content}</div></section>'

def card(p, preview=False):
    search = e(' '.join([p['title'],p['desc'],p['kind'],CATEGORIES[p['cat']][1]]), quote=True)
    quick = (f'<button class="link preview" type="button" data-title="{e(p["title"])}" data-detail="{e(p["desc"])}" hidden>Quick preview</button>' if preview else '')
    return f'''<article class="card" data-category="{p["cat"]}" data-search="{search}">
<a class="card-image" href="{url(p)}" tabindex="-1" aria-hidden="true">{pic(p)}</a>
<div class="card-body"><p class="kicker">{e(CATEGORIES[p["cat"]][1])}</p><h3><a href="{url(p)}">{e(p["title"])}</a></h3>
<p>{e(p["desc"])}</p><div class="card-actions"><a href="{url(p)}">View details</a>{quick}<a href="{quoteurl(p)}">Request quotation</a></div></div></article>'''

def cards(products, preview=False):
    return '<div class="cards">' + ''.join(card(p,preview) for p in products) + '</div>'

def viewer(p, hero=False):
    fallback = '' if hero else f'<img class="viewer-still" src="{image(p)}" alt="Conceptual {e(p["title"])}" width="640" height="540" loading="lazy">'
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
        f'<a class="category" href="{caturl(i)}"><span>{len([p for p in PRODUCTS if p["cat"] == i]):02d} entries</span>'
        f'{pic(next(p for p in PRODUCTS if p["kind"] == FEATURED[i]))}<h3>{e(c[1])}</h3><p>{e(c[2])}</p></a>'
        for i,c in enumerate(CATEGORIES)) + '</div>'

def contact_block():
    return f'<div class="contact-cols"><div><h3>Visit</h3><address>{ADDRESS}</address><a href="{MAP}">Open in Maps</a></div><div><h3>Call or message</h3><a href="tel:+919934969351">{PHONE}</a><a href="https://wa.me/919934969351">WhatsApp</a></div><div><h3>Email</h3><a href="mailto:{EMAIL}">{EMAIL}</a></div></div>'

def quote_banner():
    return f'<div class="quote-band"><p class="kicker">Project enquiries</p><h2>Discuss your equipment requirements.</h2>{button("/quotation/","Request a Quotation")}</div>'

def build_home():
    hero_product = next(p for p in PRODUCTS if p['kind'] == 'reactor-limpet')
    hero = f'''<section class="hero">
<picture class="hero-art"><source media="(max-width: 700px)" srcset="/assets/hero-mobile.webp"><img src="/assets/hero.webp" width="1536" height="1024" alt="Concept render of a stainless steel limpet coil reactor" fetchpriority="high"></picture>
<div class="shell hero-layout"><div class="hero-copy"><p class="kicker hero-kicker">Process equipment fabrication</p>
<h1>Engineered<br>for Precision.<br><em>Built for Industry.</em></h1>
<p class="lede">Unity Engineering fabricates customized pharmaceutical, chemical and industrial process equipment, serving demanding engineering requirements since 2006.</p>
<div class="actions">{button('/products/', 'Explore Products')}{button('/quotation/', 'Request a Quotation', 'outline')}</div></div>
<div class="hero-visual">{viewer(hero_product, True)}<div class="hero-caption"><span>Limpet coil reactor</span><small>Concept visualization</small></div></div></div></section>
<div class="shell statbar"><div><b>2006</b><span>Established</span></div><div><b>45</b><span>Equipment entries</span></div><div><b>06</b><span>Equipment categories</span></div><div class="stat-location">ANKLESHWAR GIDC<br>GUJARAT, INDIA</div></div>'''
    body = hero + section('Unity Engineering','Engineering Excellence Since 2006.',
        '<div class="split-copy"><p class="lede">Based in Ankleshwar GIDC, Unity Engineering fabricates process equipment around each customer’s application, operating conditions and site requirements.</p>' + button('/about/','About Unity Engineering','outline')+'</div>','light')
    body += section('Equipment catalogue','Explore six equipment families.',category_cards(), 'light')
    body += section('Featured equipment','Key equipment for process operations.',cards([next(p for p in PRODUCTS if p['kind'] == kind) for kind in FEATURED[:3]]), action=button('/products/','View all equipment','outline'))
    body += section('Interactive 3D','Inspect the equipment from every angle.',viewer(hero_product)+'<p class="caption">Concept model · Illustrative geometry</p><div class="viewer-links">'+''.join(button(url(p),p['title'],'outline') for p in PRODUCTS if p['kind'] in FEATURED)+'</div>')
    process = '<div class="story"><img src="/assets/fabrication/welding.webp" alt="Concept image of a welder joining metal components" width="620" height="410" loading="lazy"><div><h3>From drawing to dispatch.</h3><p>Engineering, forming, joining, finishing and inspection are coordinated around the agreed project scope.</p>'+button('/manufacturing/','Explore fabrication','outline')+'</div></div>'
    body += section('Manufacturing','A process shaped by the specification.',process,'light')
    body += section('Applications','Equipment for process industries.','<p class="lede">Pharmaceuticals, API manufacturing, chemicals, food processing and other industrial applications.</p>',action=button('/industries/','View industries','outline'))
    engineering_details = [('tubesheet','Tube-side flow'),('impeller','Drive and mixing geometry'),('discharge','Drain and support interfaces')]
    quality_gallery = '<div class="image-grid engineering-details">'+''.join(
        f'<figure><img src="/assets/cinematic/{key}.webp" alt="Concept equipment detail showing {label.lower()}" width="720" height="720" loading="lazy"><figcaption>{label} · Concept detail</figcaption></figure>'
        for key,label in engineering_details)+'</div>'
    body += section('Quality assurance','Define the inspection requirements early.',
        '<p class="lede">Operating conditions, materials and interfaces inform the drawing review and inspection plan.</p>'+quality_gallery,'light',button('/quality/','Quality approach','outline'))
    body += section('Gallery','Equipment concepts in detail.', '<div class="image-grid">'+''.join(pic(p) for p in PRODUCTS if p['kind'] in FEATURED[3:])+'</div>',action=button('/gallery/','Open Equipment Gallery','outline'))
    body += section('PDF catalogue','All 45 equipment entries in one reference.',button('/assets/catalogue.pdf','Download catalogue PDF','outline')+' '+button('/catalogue/','Catalogue overview','outline'),'light')
    body += '<section class="shell">'+quote_banner()+'</section>'
    body += section('Contact','Unity Engineering, Ankleshwar.',contact_block())
    page('/', 'Unity Engineering | Process Equipment Fabricator in Ankleshwar', 'Pharmaceutical, chemical and industrial process equipment fabrication in Ankleshwar, Gujarat. Explore 45 equipment entries and request a quotation.', body)

def build_products():
    filters = '<div class="catalog-controls"><label for="search">Search equipment</label><input id="search" type="search" placeholder="Search by equipment name or type"><label for="category">Category</label><select id="category"><option value="">All categories</option>'+''.join(f'<option value="{i}">{e(c[1])}</option>' for i,c in enumerate(CATEGORIES))+'</select><p id="count" role="status">45 equipment entries</p></div>'
    dialog = '<dialog id="preview-dialog"><form method="dialog"><button class="link" aria-label="Close quick preview">Close</button></form><img width="640" height="540" alt=""><h2></h2><p></p><div class="actions"><a class="btn detail-link">View details</a><a class="btn outline quote-link">Request quotation</a></div></dialog>'
    page('/products/', 'Process Equipment Catalogue', 'Find reactors, heat exchangers, vessels, dryers, mixers and processing equipment from Unity Engineering in Ankleshwar.', intro('Equipment','Process equipment catalogue.','Browse 45 equipment entries across six categories.')+'<section class="shell catalog">'+filters+f'<p id="no-results" hidden>No equipment matches your search.</p><div id="product-grid">{cards(PRODUCTS,True)}</div>'+dialog+'</section>'+section('Equipment families','Browse by category.',category_cards(),'light'))
    for i,(slug,title,description) in enumerate(CATEGORIES):
        products = [p for p in PRODUCTS if p['cat'] == i]
        banner = f'<img src="/assets/categories/{slug}.webp" width="640" height="410" alt="Concept equipment illustrating {e(title)}">'
        page(caturl(i),title,description+' Explore '+str(len(products))+' related entries.', '<div class="shell category-hero">'+intro('Equipment category',title,description)+banner+'</div>'+section('Category equipment',f'{len(products)} catalogue entries',cards(products), 'light'), [('/products/','Products')])
    for p in PRODUCTS:
        title = p['title']
        alternate = image(p,True)
        alternate_markup = f'<figure><img src="{alternate}" width="640" height="540" loading="lazy" alt="Alternate concept view of {e(title)}"><figcaption>Alternate view · Concept visualization</figcaption></figure>' if alternate else ''
        detail = p.get('detail')
        detail_markup = (f'<figure><img src="/assets/details/{p["kind"]}.webp" width="390" height="390" alt="Concept detail of {e(detail.lower())}" loading="lazy"><figcaption>{e(detail)} · Concept detail</figcaption></figure>' if detail else '')
        gallery_class = 'product-gallery with-detail' if detail else 'product-gallery'
        gallery = f'<div class="{gallery_class}"><figure>'+pic(p)+'<figcaption>Primary view · Concept visualization</figcaption></figure>'+alternate_markup+detail_markup+'</div>'
        lead = intro(CATEGORIES[p['cat']][1], title,p['desc'])
        tech = f'''<div class="detail-grid"><div><h3>Equipment overview</h3><p>{e(p['desc'])}</p><h3>Working principle</h3><p>{e(p['principle'])}</p><h3>Industrial applications</h3><p>{e(p['application'])}</p><h3>Construction features</h3><p>{e(p['features'])}.</p></div>
<div><h3>Material options</h3><p>Materials are selected for process compatibility and as per approved engineering specifications.</p><h3>Customization</h3><p>Process interfaces, drive or support arrangements and access provisions are configured for the application.</p>
<h3>Technical specifications</h3><dl class="tech"><div><dt>Capacity or throughput</dt><dd>As per customer requirement</dd></div><div><dt>Design pressure and temperature</dt><dd>As applicable to the duty</dd></div><div><dt>Material grades and acceptance</dt><dd>As per approved engineering specifications</dd></div></dl></div></div>'''
        viz = section('Interactive equipment','Inspect the concept model.',viewer(p)+'<p class="caption">Illustrative geometry · Final construction is project-specific.</p>') if p['kind'] in FEATURED else ''
        related = [other for other in PRODUCTS if other is not p and other['cat'] == p['cat']][:3]
        product_quote = button(quoteurl(p),'Request quotation for this equipment')
        content = lead+'<div class="shell product-lead">'+product_quote+gallery+'</div>'+section('Engineering overview','Process and construction.',tech,'light')+viz+section('Related equipment','Explore related configurations.',cards(related),'light')
        schema = {'@context':'https://schema.org','@type':'Product','name':title,'description':p['desc'],'image':SITE+image(p),'category':CATEGORIES[p['cat']][1]}
        page(url(p),title,p['desc']+' Discuss your process equipment fabrication requirements with Unity Engineering in Ankleshwar.',content,[('/products/','Products'),(caturl(p['cat']),CATEGORIES[p['cat']][1])],schema)
        # Keep inbound links to V1 product URLs working.
        legacy = DIST / 'products' / (p['slug']+'.html')
        if not SITE:
            legacy.write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url={url(p)}"><title>{e(title)}</title><a href="{url(p)}">Open {e(title)}</a></html>')

def build_information():
    stages = [
        ('drawings','Engineering and drawing preparation'),('cutting','Marking and plasma cutting'),
        ('rolling','Plate rolling'),('forming','Dish end forming'),('coil','Shell, limpet coil and jacket fabrication'),
        ('welding','Nozzle fabrication, fit-up and welding'),('machining','Machining and shaft assembly'),
        ('polishing','Surface finishing, buffing and polishing'),('inspection','Inspection and testing'),
        ('dispatch','Final assembly and dispatch')]
    for slug, (label, heading, description, *sections) in PAGES.items():
        content = intro(label,heading,description)
        content += section(label,'Project considerations.', '<div class="info-grid">'+''.join(f'<article><h3>{e(h)}</h3><p>{e(t)}</p></article>' for h,t in sections)+'</div>','light')
        if slug == 'manufacturing':
            content += section('Fabrication workflow','Stages from preparation to dispatch.', '<div class="image-grid process-grid">'+''.join(f'<figure><img src="/assets/fabrication/{key}.webp" alt="Concept depiction of {e(stage.lower())}" width="620" height="410" loading="lazy"><figcaption>{e(stage)}</figcaption></figure>' for key,stage in stages)+'</div><p class="caption">Concept visualization of fabrication activities</p>')
        if slug in ('infrastructure','about'):
            content += section('Contact','Find Unity Engineering.',contact_block())
        page('/'+slug+'/',label,description,content+'<div class="shell">'+quote_banner()+'</div>')
    page('/contact/','Contact Us','Contact Unity Engineering in Ankleshwar, Gujarat for process equipment fabrication enquiries.',intro('Contact','Talk to Unity Engineering.','For equipment selection and fabrication enquiries, share your process duty and project requirements.')+section('Ankleshwar, Gujarat','Phone, email and address.',contact_block(),'light')+'<div class="shell">'+quote_banner()+'</div>')
    page('/gallery/','Equipment Gallery','Concept equipment images across the six Unity Engineering equipment families.',intro('Gallery','Equipment in detail.','Concept equipment visualizations grouped by process duty.')+''.join(section('Equipment gallery',c[1],'<div class="image-grid">'+''.join(f'<figure><a href="{url(p)}">{pic(p)}</a><figcaption><a href="{url(p)}">{e(p["title"])}</a></figcaption></figure>' for p in PRODUCTS if p['cat']==i)+'</div>') for i,c in enumerate(CATEGORIES)))
    page('/catalogue/','Download Product Catalogue','Download the Unity Engineering PDF with all six equipment categories and 45 entries.',intro('Product catalogue','The equipment reference.','A downloadable guide to all 45 Unity Engineering catalogue entries.')+section('PDF','Unity Engineering equipment catalogue.',button('/assets/catalogue.pdf','Download equipment catalogue PDF'),'light')+section('Equipment families','Browse the online catalogue.',category_cards()))
    fields = [
        ('name','Customer name','text','name',True),('company','Company name','text','organization',True),
        ('email','Email','email','email',True),('phone','Mobile number','tel','tel',True),
        ('capacity','Required capacity','text','off',False),('material','Material requirement','text','off',False),
        ('pressure','Design pressure','text','off',False),('temperature','Design temperature','text','off',False)]
    inputs = ''.join(f'<label for="{key}">{label}<input id="{key}" name="{key}" type="{kind}" autocomplete="{auto}" maxlength="150"{" required" if required else ""}></label>' for key,label,kind,auto,required in fields)
    cats = ''.join(f'<option value="{i}">{e(c[1])}</option>' for i,c in enumerate(CATEGORIES))
    options = ''.join(f'<option value="{p["slug"]}" data-category="{p["cat"]}">{e(p["title"])}</option>' for p in PRODUCTS)
    enquiry = f'''<form id="enquiry" action="/contact/"><div class="form-grid">{inputs}
<label for="equipment-category">Equipment category<select id="equipment-category" name="category"><option value="">Select a category</option>{cats}</select></label>
<label for="equipment-name">Equipment name<select id="equipment-name" name="equipment"><option value="">Select equipment</option>{options}</select></label>
<label class="wide" for="requirements">Project requirements<textarea id="requirements" name="requirements" rows="5" maxlength="1500" required></textarea></label></div>
<div class="actions"><button class="btn" type="submit" value="email" disabled>Open email draft</button><button class="btn outline" type="submit" value="whatsapp" disabled>Open WhatsApp draft</button></div><p role="status" id="form-status"></p>
<noscript><p>Use the direct email or phone links to share your enquiry.</p></noscript></form>'''
    page('/quotation/','Request a Quotation','Prepare a project enquiry for Unity Engineering and send it through your email app or WhatsApp.', intro('Project enquiry','Request a quotation.','Use this form to prepare your message. Review and send the draft in your email or WhatsApp app.')+section('Equipment enquiry','Tell us about the project.',enquiry,'light')+section('Direct enquiry','Contact Unity Engineering.',contact_block()))
    page('/404.html','Page not found','Explore the Unity Engineering equipment catalogue or return to the homepage.',intro('404','Page not found.','Use the equipment catalogue to find a product or return to the homepage.')+'<div class="shell actions">'+button('/','Back to home')+button('/products/','Browse equipment','outline')+'</div>')

if DIST.exists():
    shutil.rmtree(DIST)
shutil.copytree('public', DIST)
shutil.copyfile('src/engine.js', DIST/'assets/engine.js')
build_home()
build_products()
build_information()
paths = sorted('/' if p.parent == DIST else '/'+p.parent.relative_to(DIST).as_posix()+'/' for p in DIST.rglob('index.html'))
redirects = [f'/products/{p["slug"]}.html {url(p)} 301' for p in PRODUCTS]
(DIST/'_redirects').write_text('\n'.join(redirects)+'\n')
if SITE:
    (DIST/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
    (DIST/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{e(SITE+path)}</loc></url>' for path in paths)+'</urlset>')
else:
    (DIST/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
print(f'Built {len(paths)} routes plus custom 404 ({len(PRODUCTS)} equipment, {len(CATEGORIES)} categories)')
