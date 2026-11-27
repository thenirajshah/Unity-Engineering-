"""Create the branded print catalogue from the site's source data."""
from io import BytesIO
import json
from pathlib import Path
from PIL import Image
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfgen import canvas

products = json.loads(Path('src/products.json').read_text())
categories = json.loads(Path('src/categories.json').read_text())
assets = Path('public/assets')
pdf = canvas.Canvas(str(assets / 'catalogue.pdf'), pagesize=A4, pageCompression=1)
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

def text(x,y,value,size=11,color=black,font='Helvetica'):
    pdf.setFont(font,size)
    pdf.setFillColor(color)
    pdf.drawString(x,y,value)

def footer(page):
    pdf.setStrokeColor(orange)
    pdf.line(42,67,width-42,67)
    text(42,49,'UNITY ENGINEERING  /  ANKLESHWAR GIDC',8,gray,'Helvetica-Bold')
    text(42,34,'Nirajkumarshah17@gmail.com   |   +91 9934969351',9,gray)
    text(width-57,49,str(page),8,gray,'Helvetica-Bold')

pdf.setFillColor(black)
pdf.rect(0,0,width,height,fill=1,stroke=0)
pdf.setFillColor(orange)
pdf.rect(42,306,width-84,3,fill=1,stroke=0)
text(42,362,'PRECISION FABRICATION',19,white,'Helvetica-Bold')
text(42,332,'Engineered for performance.',14,white)
pdf.drawImage(logo,42,755,38,42,mask='auto',preserveAspectRatio=True)
text(91,777,'UNITY ENGINEERING',14,white,'Helvetica-Bold')
text(91,758,'ENGINEERING EXCELLENCE SINCE 2006',9,orange,'Helvetica-Bold')
text(42,260,'Process Equipment',34,white,'Helvetica-Bold')
text(42,220,'Catalogue',34,white,'Helvetica-Bold')
text(42,188,f'{len(products)} EQUIPMENT ENTRIES',10,orange,'Helvetica-Bold')
for i,line in enumerate(simpleSplit('Unity Engineering fabricates customized pharmaceutical, chemical and industrial process equipment. Owner: Niraj Kumar Shah.', 'Helvetica', 11, width-84)):
    text(42,155-i*17,line,11,white)
text(42,82,'Plot No. 5122, 4th S Rd, Ankleshwar GIDC, Ankleshwar, Gujarat 393002, India',10,white)
text(42,62,'Nirajkumarshah17@gmail.com  |  +91 9934969351',10,white)
pdf.showPage()

page = 1
for i, (_,category,description) in enumerate(categories):
    rows = [p for p in products if p['cat'] == i]
    for start in range(0,len(rows),8):
        page += 1
        text(42,793,'EQUIPMENT CATALOGUE',10,HexColor('#A13400'),'Helvetica-Bold')
        text(42,763,category,24,black,'Helvetica-Bold')
        text(42,738,description,11,gray)
        for index,p in enumerate(rows[start:start+8]):
            col,row = index%2,index//2
            x = 42 + col * 263
            y = 710 - row * 150
            approval = p.get('approved_image')
            if approval:
                with Image.open(assets/approval['asset']) as image:
                    pdf.drawImage(jpeg(image), x,y-75,245,75,preserveAspectRatio=True,mask='auto')
                caption = approval['label']
                if approval.get('source'):
                    caption += ' / ' + approval['credit'] + ' / ' + approval['licence']
                    pdf.linkURL(approval['source'], (x,y-96,x+245,y-77))
                for line_index,line in enumerate(simpleSplit(caption,'Helvetica',7,245)):
                    text(x,y-84-line_index*8,line,7,gray)
            else:
                pdf.setFillColor(HexColor('#EFF1F3'))
                pdf.rect(x,y-90,245,90,fill=1,stroke=0)
                text(x+12,y-48,'Image pending',10,gray)
            for j,line in enumerate(simpleSplit(p['title'],'Helvetica-Bold',11,245)):
                text(x,y-106-j*13,line,11,black,'Helvetica-Bold')
        text(42,86,'Configuration as per approved engineering specifications',8,gray)
        footer(page)
        pdf.showPage()
pdf.save()
