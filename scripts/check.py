"""Check the generated site without a browser or external services."""
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import hashlib
import json
import subprocess
import re

out = Path('dist')
products = json.loads(Path('src/products.json').read_text())
cats = json.loads(Path('src/categories.json').read_text())
pages = list(out.rglob('index.html')) + [out/'404.html']
titles = set()
descriptions = set()

class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()
        self.headings = 0
        self.title = ''
        self.in_title = False
        self.description = None

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if 'id' in data:
            assert data['id'] not in self.ids, f'Duplicate ID {data["id"]}'
            self.ids.add(data['id'])
        if tag == 'h1':
            self.headings += 1
        if tag == 'title':
            self.in_title = True
        if tag == 'meta' and data.get('name') == 'description':
            self.description = data.get('content')
        if tag == 'img':
            assert 'alt' in data and 'width' in data and 'height' in data
        self.links.extend(data[key] for key in ('src','href','srcset') if key in data)

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data

assert len(products) == 23
assert len(pages) == 43
for path in pages:
    document = Document()
    document.feed(path.read_text())
    assert document.headings == 1, path
    assert document.title and document.title not in titles, path
    assert document.description and document.description not in descriptions, path
    titles.add(document.title)
    descriptions.add(document.description)
    for link in document.links:
        target = urlsplit(link)
        if target.fragment and not target.path:
            assert target.fragment in document.ids, (path,link)
        if not target.path.startswith('/') or target.netloc:
            continue
        relative = target.path.lstrip('/')
        file = out/relative
        assert file.is_file() or (file/'index.html').is_file(), (path,link)

image_hashes = set()
for p in products:
    approved = p['approved_image']
    asset = out/'assets'/approved['asset']
    digest = hashlib.sha256(asset.read_bytes()).hexdigest()
    assert digest not in image_hashes, p['slug']
    image_hashes.add(digest)
    content = (out/'products'/p['slug']/'index.html').read_text()
    assert f'/assets/{approved["asset"]}' in content
    assert approved['label'] in content and 'Image pending' not in content
    for heading in ('Working principle','Industrial applications','Construction features','Material options','Technical specifications'):
        assert heading in content, (p['slug'],heading)
for slug,*_ in cats:
    assert (out/'products/categories'/slug/'index.html').is_file(), slug
for path in out.rglob('*'):
    assert path.suffix != '.svg', path
    if path.suffix == '.glb':
        content = path.read_bytes()
        assert content[:4] == b'glTF'
        assert int.from_bytes(content[8:12],'little') == len(content)
        length = int.from_bytes(content[12:16],'little')
        asset = json.loads(content[20:20+length])
        assert asset['asset']['version'] == '2.0'
        assert asset['accessors'][3]['count'] % 3 == 0
pdf = out/'assets/catalogue.pdf'
assert pdf.read_bytes().startswith(b'%PDF-')
extracted = subprocess.check_output(['pdftotext', str(pdf), '-'], text=True)
normalize = lambda value: re.sub(r'\s+', ' ', value)
for p in products:
    assert normalize(p['title']) in normalize(extracted), p['title']
industry_titles = [industry[1] for industry in json.loads(Path('src/industries.json').read_text())]
for path in ('index.html','industries/index.html'):
    content = (out/path).read_text()
    assert 'Solutions for Critical Manufacturing Environments' in content
    for title in industry_titles:
        assert escape(title) in content
assert next(p for p in products if p['slug'] == 'autoclave-reactors')['cat'] == 0
assert sum(p['cat'] == 2 for p in products) == 1
redirects = json.loads(Path('src/redirects.json').read_text())
for old,new in redirects.items():
    assert f'{old} {new} 301' in (out/'_redirects').read_text()
    assert not (out/old.strip('/')/'index.html').exists(), old
    assert (out/new.strip('/')/'index.html').exists(), new
for folder in ('renders','products','categories','details'):
    assert not (out/'assets'/folder).exists()
print(f'Verified {len(pages)} pages, 23 PDF entries, industries, redirects, image gating and GLB headers.')
