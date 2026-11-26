"""Optimize locally rendered masters and create a source and rights manifest."""
import csv
import json
from pathlib import Path
from PIL import Image, ImageFilter

assets = Path('public/assets')
renders = assets / 'renders'
renders.mkdir(exist_ok=True)
source = Path('/tmp/unity-render')
for master in source.glob('*.png'):
    out = renders / (master.stem + '.webp')
    if not out.exists():
        try:
            with Image.open(master) as image:
                image.convert('RGB').filter(ImageFilter.SMOOTH).save(out, quality=85, method=6)
        except OSError:
            continue

products = json.loads(Path('src/products.json').read_text())
by_kind = {p['kind']:p['title'] for p in products}

with Path('ASSETS.csv').open('w', newline='', encoding='utf-8') as stream:
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(['File','Source','Licence or rights basis','Equipment / subject','Type','Verification status'])
    for path in sorted(assets.rglob('*')):
        if not path.is_file():
            continue
        kind = path.stem.removesuffix('-alt').removesuffix('-hero').removesuffix('-cutaway').removesuffix('-exploded')
        if path.parent.name in ('renders','models'):
            label = 'Alternate view' if path.stem.endswith('-alt') else '3D GLB' if path.suffix == '.glb' else 'Primary view'
            source_name = 'V1 mesh adapted for V2 / Blender' if path.suffix != '.glb' else 'Original procedural geometry exported as glTF'
            row = (source_name,'Project-created and user-supplied source',by_kind.get(kind,kind),label,'Concept geometry; requires engineering review')
        elif path.parent.name == 'categories':
            row = ('V2 Blender alternate view cropped for category banner','Project-created from V1 geometry',path.stem,'Category banner','Concept geometry; requires engineering review')
        elif path.parent.name in ('fabrication','details','cinematic') or path.stem.startswith('hero'):
            row = ('OpenAI image generation for Unity Engineering','Project-generated output',by_kind.get(kind,{'fabrication':'Fabrication workflow','cinematic':path.stem}.get(path.parent.name,'Limpet coil reactor')),'Concept image','Editorial concept; facility and equipment details unverified')
        elif path.parent.name == 'products':
            row = ('Supplied V1 archive','User-supplied project artwork',by_kind.get(kind,kind),'Fallback render','Original concept from V1')
        elif path.suffix == '.pdf':
            row = ('Unity Engineering V2 catalogue','Project-created and user-supplied source','45 equipment entries','Catalogue','Catalogue count verified; renders conceptual')
        elif path.suffix in ('.png','.webp'):
            row = ('Supplied V1 archive','User-supplied brand assets','Unity Engineering','Brand asset','Original geometry')
        else:
            continue
        writer.writerow([path.relative_to('public'),*row])
