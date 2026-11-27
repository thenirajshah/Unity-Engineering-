"""Create the branded print catalogue from the site's source data."""
from io import BytesIO
import json
from pathlib import Path
from PIL import Image
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

products = json.loads(Path('src/products.json').read_text())
categories = json.loads(Path('src/categories.json').read_text())
assets = Path('public/assets')
regular = 'Catalogue Sans'
bold = 'Catalogue Sans Bold'
pdfmetrics.registerFont(TTFont(regular, 'Vera.ttf'))
pdfmetrics.registerFont(TTFont(bold, 'VeraBd.ttf'))
pdf = canvas.Canvas(str(assets / 'catalogue.pdf'), pagesize=A4, pageCompression=1, initialFontName=regular)
pdf.setTitle('Unity Engineering | Process Equipment Catalogue')
pdf.setAuthor('Unity Engineering')
width,height = A4
orange = HexColor('#FF5500')
black = HexColor('#101316')
gray = HexColor('#4B555D')
logo = ImageReader(str(assets / 'logo.png'))

def jpeg(image):
    output = BytesIO()
    image.convert('RGB').save(output, format='JPEG', quality=82, optimize=True)
    output.seek(0)
    return ImageReader(output)

def text(x,y,value,size=11,color=black,font=regular):
    pdf.setFont(font,size)
    pdf.setFillColor(color)
    pdf.drawString(x,y,value)

def footer(page):
    pdf.setStrokeColor(orange)
    pdf.line(42,67,width-42,67)
    text(42,49,'UNITY ENGINEERING  /  ANKLESHWAR GIDC',8,gray,bold)
    text(42,34,'Nirajkumarshah17@gmail.com   |   +91 9934969351',9,gray)
    text(width-57,49,str(page),8,gray,bold)

pdf.setFillColor(black)
pdf.rect(0,0,width,height,fill=1,stroke=0)
pdf.setFillColor(orange)
pdf.rect(42,306,width-84,3,fill=1,stroke=0)
text(42,362,'PRECISION FABRICATION',19,white,bold)
text(42,332,'Engineered for performance.',14,white)
pdf.drawImage(logo,42,755,38,42,mask='auto',preserveAspectRatio=True)
text(91,777,'UNITY ENGINEERING',14,white,bold)
text(91,758,'ENGINEERING EXCELLENCE SINCE 2006',9,orange,bold)
text(42,260,'Process Equipment',34,white,bold)
text(42,220,'Catalogue',34,white,bold)
text(42,188,f'{len(products)} EQUIPMENT ENTRIES',10,orange,bold)
for i,line in enumerate(simpleSplit('Unity Engineering fabricates customized pharmaceutical, chemical and industrial process equipment. Owner: Niraj Kumar Shah.', regular, 11, width-84)):
    text(42,155-i*17,line,11,white)
text(42,82,'Plot No. 5122, 4th S Rd, Ankleshwar GIDC, Ankleshwar, Gujarat 393002, India',10,white)
text(42,62,'Nirajkumarshah17@gmail.com  |  +91 9934969351',10,white)
pdf.showPage()

page = 1
for i, (category_slug, category, _) in enumerate(categories):
    for index, product in enumerate(p for p in products if p['cat'] == i):
        page += 1
        if index == 0:
            pdf.bookmarkPage(category_slug)
            pdf.addOutlineEntry(category, category_slug, level=0, closed=True)
        pdf.bookmarkPage(product['slug'])
        pdf.addOutlineEntry(product['title'], product['slug'], level=1)
        text(42,793,category.upper(),10,HexColor('#A13400'),bold)
        available_width = width - 84
        title_lines = simpleSplit(product['title'], bold, 26, available_width)
        for line_index, line in enumerate(title_lines):
            text(42,755-line_index*31,line,26,black,bold)

        image_bottom = 171
        image_height = 735 - (len(title_lines) - 1) * 31 - image_bottom
        approval = product.get('approved_image')
        pdf.setFillColor(HexColor('#EFF1F3'))
        pdf.rect(42,image_bottom,available_width,image_height,fill=1,stroke=0)
        if approval:
            with Image.open(assets/approval['asset']) as image:
                pdf.drawImage(jpeg(image), 42,image_bottom,available_width,image_height,
                              preserveAspectRatio=True, mask='auto')
            caption = approval['label']
            if approval.get('source'):
                caption += ' / ' + approval['credit'] + ' / ' + approval['licence']
            caption_lines = simpleSplit(caption, regular, 9, available_width)
            for line_index, line in enumerate(caption_lines):
                text(42,154-line_index*11,line,9,gray)
            if approval.get('source'):
                pdf.linkURL(approval['source'], (42,150-len(caption_lines)*11,width-42,165))
        else:
            text(57,image_bottom+image_height/2,'Image pending',11,gray)
        for line_index, line in enumerate(simpleSplit(product['desc'], regular, 12, available_width)):
            text(42,120-line_index*16,line,12,gray)
        footer(page)
        pdf.showPage()
pdf.save()
