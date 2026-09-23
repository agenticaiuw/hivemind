import json
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

BASE = Path(__file__).parent
DATA = json.loads((BASE / 'purchased-components.json').read_text())
ADD = json.loads((BASE / 'additions-components.json').read_text())['additions']
OUT = Path('/Users/evanliu/agentic-gadget/outputs/01a0d046-7d49-7871-8a87-73ebb2cf093f/Agentic_AI_UW_Component_Costs.docx')
doc = Document()
for border in doc.styles.element.xpath('.//w:pBdr'):
    border.getparent().remove(border)
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.5), Inches(11)
sec.top_margin = sec.bottom_margin = Inches(.65)
sec.left_margin = sec.right_margin = Inches(.65)
sec.footer_distance = Inches(.28)
for name in ['Normal', 'Title', 'Subtitle', 'Heading 1', 'Heading 2']:
    st = doc.styles[name]
    st.font.name = 'Calibri'
    st.font.color.rgb = RGBColor(0, 0, 0)
doc.styles['Normal'].font.size = Pt(11)
doc.styles['Normal'].paragraph_format.space_after = Pt(7)
doc.styles['Normal'].paragraph_format.line_spacing = 1.06
doc.styles['Title'].font.size = Pt(25)
doc.styles['Title'].paragraph_format.space_after = Pt(7)
doc.styles['Heading 1'].font.size = Pt(18)
doc.styles['Heading 1'].paragraph_format.space_before = Pt(0)
doc.styles['Heading 1'].paragraph_format.space_after = Pt(9)
doc.styles['Heading 2'].font.size = Pt(13)
doc.styles['Heading 2'].paragraph_format.space_before = Pt(11)
doc.styles['Heading 2'].paragraph_format.space_after = Pt(5)
doc.core_properties.title = 'Agentic AI UW Device Component Costs'
doc.core_properties.author = 'Agentic AI UW'
doc.core_properties.subject = 'Purchased hardware and component pricing for UW Madison ECE review'

def link(p, text, url):
    h = OxmlElement('w:hyperlink')
    h.set(qn('r:id'), p.part.relate_to(url, RT.HYPERLINK, is_external=True))
    r = OxmlElement('w:r'); pr = OxmlElement('w:rPr')
    c = OxmlElement('w:color'); c.set(qn('w:val'), '175E78'); pr.append(c)
    u = OxmlElement('w:u'); u.set(qn('w:val'), 'single'); pr.append(u)
    r.append(pr); t = OxmlElement('w:t'); t.text = text; r.append(t); h.append(r); p._p.append(h)

def para(text='', bold=None):
    after_table = len(doc._element.body) > 1 and doc._element.body[-2].tag == qn('w:tbl')
    p = doc.add_paragraph()
    if after_table and text:
        p.paragraph_format.space_before = Pt(7)
    if bold and text.startswith(bold):
        p.add_run(bold).bold = True; p.add_run(text[len(bold):])
    else: p.add_run(text)
    return p

def table(headers, widths, rows, size=10):
    t = doc.add_table(rows=1, cols=len(headers)); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for col, w in zip(t.columns, widths): col.width = Inches(w)
    for c, h in zip(t.rows[0].cells, headers): c.text = h
    rep = OxmlElement('w:tblHeader'); t.rows[0]._tr.get_or_add_trPr().append(rep)
    for row in rows:
        cells = t.add_row().cells
        for c, val in zip(cells, row):
            p = c.paragraphs[0]
            if isinstance(val, list):
                for i, chunk in enumerate(val):
                    if i: p.add_run('\n')
                    if isinstance(chunk, tuple): link(p, *chunk)
                    else: p.add_run(chunk)
            else: p.add_run(str(val))
    for ri, row in enumerate(t.rows):
        trpr = row._tr.get_or_add_trPr(); ns = OxmlElement('w:cantSplit'); trpr.append(ns)
        for ci, cell in enumerate(row.cells):
            cell.width = Inches(widths[ci]); cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tcpr = cell._tc.get_or_add_tcPr()
            borders = OxmlElement('w:tcBorders')
            for side in ['top','left','bottom','right']:
                b = OxmlElement('w:'+side); b.set(qn('w:val'),'single'); b.set(qn('w:sz'),'4'); b.set(qn('w:color'),'D9D9D9'); borders.append(b)
            tcpr.append(borders)
            mar = OxmlElement('w:tcMar')
            for side, value in [('top',75),('bottom',75),('left',90),('right',90)]:
                e = OxmlElement('w:'+side); e.set(qn('w:w'), str(value)); e.set(qn('w:type'),'dxa'); mar.append(e)
            tcpr.append(mar)
            if ri == 0:
                sh = OxmlElement('w:shd'); sh.set(qn('w:fill'),'E8EEF1'); tcpr.append(sh)
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
                if ci == 0 and len(headers)>3: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for r in p.runs:
                    r.font.size = Pt(size); r.bold = ri == 0
                # Hyperlink runs do not appear in python-docx paragraph.runs.
                for rpr in p._p.xpath('.//w:hyperlink/w:r/w:rPr'):
                    sz=OxmlElement('w:sz'); sz.set(qn('w:val'),str(int(size*2))); rpr.append(sz)
    return t

f = sec.footer.paragraphs[0]; f.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r=f.add_run('Agentic AI UW  |  '); r.font.size=Pt(9)
fld=OxmlElement('w:fldSimple'); fld.set(qn('w:instr'),'PAGE'); f._p.append(fld)

doc.add_paragraph('Agentic AI UW Device Component Costs', 'Title')
para('For UW–Madison Electrical and Computer Engineering • 23 September 2026')
para('Our prototype purchases total $268.80 in hardware and $331.60 after tariffs, shipping, and tax. The lists below compare those purchases with components for a custom PCB and price the requested camera, fingerprint, cellular calling and texting, contactless payment, and solar additions.')
doc.add_heading('1 Purchased boards and components', 1)
para('Actual July 2026 receipt prices, USD. One of each item was purchased. Linked product names identify the hardware; today’s store price may differ from the receipt.')
short = ['MAX98357A I2S 3 W amplifier breakout','PDM MEMS microphone breakout','DRV2605L haptic driver breakout','Vibrating mini motor disc','LiPo battery 3.7 V 500 mAh','Mini oval speaker 8 Ω 1 W','LSM6DSOX six-axis IMU breakout','Nordic nRF9160 Development Kit','HUZZAH32 ESP32 Feather with loose headers','microSD breakout 5 V or 3 V','DFRobot FIT0642 64 GB Class 10 microSD card']
rows=[]
for i,(p,n) in enumerate(zip(DATA['purchased'],short),1):
    rows.append([i,[(n,p['product_url'])],f"${p['paid_unit']:.2f}", 'A' if i<=7 else ('B' if i==8 else 'C')])
table(['Item','Purchased product','Paid each','Receipt'], [.42,5.0,.93,.85],rows)
para('')
table(['Receipt','Date','Hardware','Total paid'], [3.8,1.1,1.1,1.2], [
    ['A  Adafruit 3705537','Jul 2, 2026','$42.65','$64.37'],
    ['B  DigiKey 128558494','Jul 2, 2026','$179.80','$210.12'],
    ['C  DigiKey 128923808','Jul 9, 2026','$46.35','$57.11'],
    ['Total','',' $268.80','$331.60']])
para('The $62.80 above hardware consists of $17.17 in tariffs, $28.34 in shipping, and $17.29 in sales tax. These are prior purchases, separate from a future 30-device manufacturing order.')

doc.add_page_break()
doc.add_heading('2 Bare chips and corresponding components',1)
para('Current public one-unit prices checked 23 September 2026, in USD, before tax, shipping, and tariffs. Item numbers match the purchased list. Packaged ICs are shown where available; modules and physical parts are identified explicitly.')
B = {x['purchased_id']:x for x in DATA['bare'] if x['type'] not in ['bare microphone alternative', 'bare SoC']}
mic_alt=next(x for x in DATA['bare'] if x['purchased_id']=='mic' and x['unit_price'] is not None)
def bval(k,label=None):
    x=B[k]; return [(label or x['name'],x['url'])]
rows=[
    [1,bval('amp','MAX98357AETE+T'),'$4.08','Amplifier IC; same core part.'],
    [2,[("MP34DT01TR-M",next(x['url'] for x in DATA['bare'] if x['purchased_id']=='mic' and x['unit_price'] is None)),('TDK MMICT5838-00-012',mic_alt['url'])], 'No quote\n$2.67 alt.','Original microphone obsolete. TDK alternative requires a new footprint, power and acoustic validation.'],
    [3,bval('haptic_driver','DRV2605LDGSR'),'$2.10','Haptic driver IC; motor is separate.'],
    [4,bval('motor','Mini motor disc'),'$1.95','Complete actuator; no bare chip equivalent.'],
    [5,bval('battery','3.7 V 500 mAh LiPo pack'),'$7.95','Complete battery pack; no bare chip equivalent.'],
    [6,bval('speaker','8 Ω 1 W oval speaker'),'$1.95','Complete speaker; no bare chip equivalent.'],
    [7,bval('imu','LSM6DSOXTR'),'$5.30','Sensor IC; listed price, no immediate distributor stock.'],
    [8,bval('cellular','NRF9160-SICA-B1A-R7'),'$31.56','Cellular/GNSS system in package. Same family; verify DK revision.'],
    [9,bval('esp32','ESP32-WROOM-32E-N4'),'$4.99','RF module with flash and antenna. Comparable WROOM revision, not verified identical.'],
    [10,bval('sd_breakout','GCT MEM2090-00-145-00-A'),'$1.50','microSD socket alternative; excludes regulator and level shifting.'],
    [11,bval('sd_card','DFRobot FIT0642 64 GB card'),'$18.90','Complete memory card; listed price, no immediate stock.'],
]
soc=next((x for x in DATA['bare'] if x.get('type')=='bare SoC'),None)
if soc:
    rows.insert(9,[9,[(soc['name'],soc['url'])],f"${soc['unit_price']:.2f}",'Bare ESP32 SoC candidate; needs flash, clock, RF and power circuitry.'])
table(['Item','Component and supplier link','Each','What the price covers'],[.42,2.62,.88,3.28],rows,10)
para('')
para('Support circuitry remains necessary. Chip prices exclude the PCB, passives, regulators, connectors, RF layout, antennas, soldering, assembly, and test. A socket is not a memory card, and a cellular module is not a complete phone.',bold='Support circuitry remains necessary.')
para('The original microphone has no current distributor quote. Its alternative is not a drop-in replacement. A sum of this column would therefore not represent a complete, equivalent production bill of materials.')

doc.add_page_break()
doc.add_heading('3 Camera fingerprint and solar additions',1)
para('Public one-unit USD prices. Prototype boards and compact components are alternatives for the same function, so their prices should not be added together.')
rows=[]
for i in [0,1,2,3]:
    a=ADD[i]
    if i==2:
        rows.append(['Solar panel', [('Voltaic P122 panel',a['board_url'])],'$5.95',[('Same panel on custom device',a['board_url'])],'$5.95'])
    else:
        labels=[('Arducam B006701 SPI camera','OV2640 M0031 lens/FPC assembly'),('SparkFun FPC2534 Qwiic','FPC2534AP LGA sensor system'),None,('Adafruit BQ24074 charger','TI BQ24074RGTR charger IC')][i]
        rows.append([['Camera','Fingerprint','Solar panel','Solar charger'][i],[(labels[0],a['board_url'])],f"${a['board_price']:.2f}",[(labels[1],a['bare_url'])],f"${a['bare_price']:.2f}"])
table(['Function','Prototype board or module','Each','Compact component','Each'],[.85,2.15,.65,2.85,.7],rows)
doc.add_heading('Camera',2)
para('The $25.99 camera board uses SPI and has an onboard image buffer. The $6.99 OV2640 option includes the sensor, lens, and flexible cable; it is not a bare image sensor. Its parallel DVP interface requires different wiring and firmware. Bare sensor pricing requires an OEM quote.')
doc.add_heading('Fingerprint',2)
para('The $59.95 Qwiic board and $23.85 FPC2534AP LGA component form a matched comparison. The LGA package contains a fingerprint sensor and processing system. At the published 25-unit tier, prices are $53.96 per board and $20.1156 per LGA component; 30 units would be $1,618.80 or $603.47 before tax and shipping.')
p=para('A lower-cost prototype option is the '); link(p,'Adafruit optical UART fingerprint module', 'https://www.adafruit.com/product/4690'); p.add_run(' at $19.95. It is a different, bulkier assembly. Fingerprint matching by itself does not enable or certify payments.')
doc.add_heading('Solar panel and charging',2)
para('The $5.95 panel measures 52 × 52 × 3.1 mm and is rated about 0.3 W outdoors, with approximately 5.9 V and 50 mA at maximum power. It may be too large for a small wearable face. Actual harvested energy depends on light and orientation; indoor output will be much lower.')
p=para('The panel plus charger board costs $20.90 before the battery. On a custom PCB, the same panel plus the $2.43 charger IC costs $8.38 before support circuitry. The BQ24074 board is intended for 6–7 V panels; validate this panel pairing, charge current, and battery protection on the bench. '); link(p,'Panel dimensions and electrical data',ADD[2]['bare_url'])
para('For a 30-device build, the charger IC’s published 25-unit tier is $1.6496 each. These price tiers are useful planning references; they do not establish a complete manufacturing cost or stock allocation.')

doc.add_page_break()
doc.add_heading('4 Calls texts and contactless payments',1)
para('The cellular addition is for placing and receiving calls and texts. The payment addition is for the wearer to pay at contactless terminals. Both require service enablement beyond purchasing electronics.')
doc.add_heading('Cellular voice and SMS',2)
table(['Implementation','Linked hardware','Public unit price'],[1.5,4.25,1.45],[
    ['Prototype board',[('Waveshare SIM7600NA-H 4G HAT','https://www.waveshare.com/sim7600na-h-4g-hat.htm')],'$84.99 USD'],
    ['Solder-down module',[('SIMCom SIM7600NA-H at LCSC','https://www.lcsc.com/product-image/C5380303.html?whichImg=sch')],'$42.71 USD'],
])
para('')
p=para('The HAT exposes the modem for prototyping and includes the board interfaces. The solder-down part is a cellular modem module, not a single bare IC; a custom product still needs a SIM interface, antennas, power supply, audio interfaces, PCB, and integration. '); link(p,'SIMCom SIM7600-H family specifications','https://www.simcom.com/product/SIM7600X-H.html')
para('A phone number comes from a carrier’s voice/SMS subscription. Verify that the chosen carrier supports this exact module, firmware, and VoLTE service before ordering 30. A data-only SIM does not establish calling support. Treat SIM activation and recurring service as a separate carrier quote.')
para('The LCSC one-unit listing was $42.7074, rounded above; its 10-unit tier was $41.6486, but only two units were shown in stock. The HAT is about 56 × 65 mm and the module about 30 × 30 mm, so these are development candidates requiring a size and power review for a wearable.')
doc.add_heading('Contactless payment hardware',2)
table(['Implementation','Linked product','Price status'],[1.5,4.25,1.45],[
    ['Payment chip or module',[('Infineon SECORA Pay W','https://www.infineon.com/products/security-smart-card-solutions/secora-security-solutions/secora-pay')],'Supplier quote required'],
    ['Working sample hardware',[('USC Wearable Technology Samples Pack USC-SAMPLE-03','https://www.usmartcards.co.uk/sample-and-oem-packs/usc-wearable-technology-samples-pack')],'£99 GBP per pack, excl. VAT'],
])
para('')
p=para('SECORA Pay W targets passive payment wearables and is offered in a packaged chip or insertable payment-module format. A production price requires a supplier quote covering the part, payment software, and provisioning route. '); link(p,'Infineon wearable payment integration','https://www.infineon.com/applications/security-solutions/payment-solutions/wearable-payments')
para('The £99 sample pack is an integration reference containing assorted wearables and payment inserts, not a per-chip price or a general-purpose breakout board. Its listed activation path uses Curve and DIGISEQ. Confirm the exact contents and eligibility of the intended US users, banks, and cards before purchase; the pack does not establish support for this club’s deployment.')
para('A generic NFC reader such as PN532 is not a provisioned payment credential. Antenna tuning, credential provisioning, supported issuers, and payment-program approval remain separate requirements. Request both per-device and setup fees in the supplier quote.')

OUT.parent.mkdir(parents=True,exist_ok=True)
doc.save(OUT)
print(OUT)
