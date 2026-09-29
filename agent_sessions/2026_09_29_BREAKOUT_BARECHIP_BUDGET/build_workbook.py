#!/usr/bin/env python3
"""Minimal 2-sheet Hivemind budget. Data-driven from components.json, compute-options.json,
manufacturing.json (rich data stays in those files). Re-run after any of them changes."""
import json, os
from urllib.parse import urlparse
from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, "Hivemind_Hardware_Budget.xlsx")
ACC = "1F4E5A"; SOFT = "E8F0F2"
F = lambda **k: Font(name="Arial", size=k.pop("size", 10), **k)
BLUE = F(color="0000FF"); BLK = F(); BOLD = F(bold=True); LINK = F(color=ACC, underline="single")
HDR = F(bold=True, color="FFFFFF"); HFILL = PatternFill("solid", fgColor=ACC); SFILL = PatternFill("solid", fgColor=SOFT)
TOP = Border(top=Side(style="medium", color=ACC))
USD = '$#,##0.00;($#,##0.00);"-"'
load = lambda n: json.load(open(os.path.join(D, n))) if os.path.exists(os.path.join(D, n)) else []

comp = load("components.json") + load("compute-options.json")
M = load("manufacturing.json"); dev = M["development"]["items"]; mfg = M["manufacturing"]["items"]

def part(sub):
    for r in comp:
        if sub.lower() in r["name"].lower(): return r
    raise KeyError(sub)
def devi(sub):
    for r in dev:
        if r["item"].lower().startswith(sub.lower()): return r
    raise KeyError(sub)
def mfi(stage, sub=""):
    for r in mfg:
        if r["stage"] == stage and sub.lower() in r["item"].lower(): return r
    raise KeyError(stage)

# (label, kind, source-substring, cell comment override)
ROWS = [
 ("Components", None),
 ("Processing chip (cellular)", part("nRF9151 DK")),
 ("Bluetooth chip", part("nRF54LM20 DK")),
 ("Wi-Fi chip", part("nRF7002 EK")),
 ("Flash storage", part("XTSD 2 GB")),
 ("Camera", part("Arducam Mini 2MP")),
 ("IMU", part("SparkFun 6DoF IMU BMI270")),
 ("Fingerprint sensor", part("UART Fingerprint Sensor (D)")),
 ("Wireless charging (MagSafe-compatible Qi)", part("Universal Qi Receiver")),
 ("USB-C charging", part("Micro-Lipo Charger USB-C")),
 ("Battery charge monitoring (fuel gauge)", part("MAX17048 fuel gauge")),
 ("Battery management (charger/protection)", part("nPM1304 EK")),
 ("Battery", part("LiPo 3.7 V 350 mAh")),
 ("Haptic driver", part("DRV2605L haptic driver")),
 ("Buzzer", part("piezo buzzer")),
 ("Microphone", part("PDM MEMS mic breakout")),
 ("Amplifier", part("MAX98357A I2S amp")),
 ("Speaker", part("mini oval speaker")),
 ("E-ink display", part("2.9in e-Paper module")),
 ("Touch sensor", part("AT42QT1070 5-pad")),
 ("Stylus", part("capacitive-touch e-Paper")),
 ("3D printing", devi("3D-printed pendant shells")),
 ("Metal casting / CNC", devi("CNC aluminum shell samples")),
 ("Watch band", devi("Watch-band")),
 ("Necklace", devi("Necklace cord")),
 ("Testing", None),
 ("Breadboard", devi("Breadboards")),
 ("Jumper wires", devi("Jumper wires")),
 ("Agentic coding subscriptions", "subs"),
 ("PCB design software", devi("KiCad")),
 ("3D CAD software", devi("Onshape")),
 ("Voice tokens", devi("OpenAI gpt-realtime-2.1-mini")),
 ("Full prototype units", "proto"),
 ("Tools", None),
 ("Soldering station", devi("Pinecil")),
 ("Magnifier", devi("Stereo/digital soldering microscope")),
 ("Clamp", devi("Helping hands")),
]

wb = Workbook(); wc = wb.active; wc.title = "Components"; wm = wb.create_sheet("Manufacturing (30 units)")
MS = "'Manufacturing (30 units)'!"

# ---------------- Manufacturing layout (row numbers fixed so Components can reference the BOM row)
R = dict(starts=2, acc=3, target=4, pcb=6, pcba=7, comp=8, encl=9, band=10, cable=11, pack=12, ship=13, other=14, sub=15, cont=16, tot=17, per=18)

# ---------------- Components sheet
hdr = ["Name", "Estimate Cost", "Estimated Units for Testing", "Product Link", "Product Name", "Actual Product Price"]
for i, (h, w) in enumerate(zip(hdr, [40, 14, 14, 22, 40, 16]), 1):
    c = wc.cell(1, i, h); c.font = HDR; c.fill = HFILL; c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="left" if i == 1 else "center")
    wc.column_dimensions["ABCDEF"[i - 1]].width = w
wc.row_dimensions[1].height = 34
def link(c, url):
    if url:
        c.value = urlparse(url).netloc.replace("www.", ""); c.hyperlink = url; c.font = LINK
    c.alignment = Alignment(horizontal="left", vertical="center")
def note(c, text):
    cm = Comment(text, "budget"); cm.width = 320; cm.height = 90; c.comment = cm
x = 2
for label, src in ROWS:
    if src is None:
        for j in range(1, 7): wc.cell(x, j).fill = SFILL
        wc.cell(x, 1, label).font = BOLD; x += 1; continue
    est = act = units = url = cmt = pname = None
    if src == "subs":
        est, units, act, url = 200, 8, 200, "https://claude.com/pricing"
        pname, cmt = "Claude Max 20x ($200/month)", "Units = months."
    elif src == "proto":
        est, units, act, url = 350, 4, None, devi("Prototype PCB fab")["url"]
        pname = "Complete unit: PCB + assembly + parts + shell (JLCPCB)"
        cmt = "Rough per-unit allowance. Each unit may use a different low-power chip / configuration."
    elif "item" in src:                      # manufacturing.json development item
        est, units, act, url = src["estimate_usd"], src["qty"], src["actual_price_usd"], src["url"]
        pname = src["item"]
        if label == "Voice tokens":
            est, units, act, url, pname = 0.05, 5000, 0.05, "https://openai.com/api/pricing/", "GPT Live ($0.05/minute)"
            cmt = "Units = minutes of testing."
    else:                                    # components.json / compute-options.json part
        est, units, act, url = src["estimate_usd"], src["units_for_testing"], src["actual_price_usd"], src["url"]
        if "OUT OF STOCK" in (src.get("notes") or ""): act = None   # listed price not orderable: leave Actual blank
        pname = src["name"]
    wc.cell(x, 1, label).font = BLK
    if cmt: note(wc.cell(x, 1), cmt)
    c = wc.cell(x, 2, est); c.font = BLK if str(est).startswith("=") else BLUE; c.number_format = USD
    c = wc.cell(x, 3, units); c.font = BLUE; c.alignment = Alignment(horizontal="center"); c.number_format = "#,##0"
    link(wc.cell(x, 4), url)
    c = wc.cell(x, 5, (pname or "").split(" (")[0].split(", ")[0]); c.font = BLK; c.alignment = Alignment(wrap_text=True, vertical="center")
    c = wc.cell(x, 6, act); c.font = BLUE; c.number_format = USD
    x += 1
last = x - 1; x += 1
rg = lambda col: f"{col}2:{col}{last}"
wc.cell(x, 1, "Total (Actual where verified, else Estimate)").font = BOLD
c = wc.cell(x, 2, f'=SUMPRODUCT({rg("C")},{rg("B")})+SUMPRODUCT({rg("C")},({rg("F")}<>"")*({rg("F")}-{rg("B")}))')
c.font = BOLD; c.number_format = USD
for j in range(1, 7): wc.cell(x, j).border = TOP
wc.freeze_panes = "B2"; wc.sheet_view.showGridLines = False
COMP_TOTAL = x

# ---------------- Manufacturing sheet
for i, (h, w) in enumerate(zip(["Item", "Unit Cost", "Quantity", "Total", "Notes"], [50, 13, 11, 14, 64]), 1):
    c = wm.cell(1, i, h); c.font = HDR; c.fill = HFILL; c.alignment = Alignment(vertical="center", horizontal="left" if i in (1, 5) else "center")
    wm.column_dimensions["ABCDE"[i - 1]].width = w
wm.row_dimensions[1].height = 26
BAD = ("BQ25180", "MAX17048", "nRF5340", "nRF9160", "PSRAM", "W25N02KV")
ADD = ("CSNP1GCR01", "TPS22916C")   # owner: SD NAND replaces W25N02KV; load switch added
terms, listing = [], []
for r in comp:
    if r["type"] == "bare" and r["per_device_qty"] and not any(k in r["name"] for k in BAD) and (
            any(k in r["part_number"] for k in ADD) or (r["required"] == "core" and r.get("project", "pendant") != "study-tool")):
        p = r["qty100_price_usd"] if r["qty100_price_usd"] is not None else (r["actual_price_usd"] if r["actual_price_usd"] is not None else r["estimate_usd"])
        terms.append(f'{p}*{r["per_device_qty"]}'); listing.append(f'{r["name"].split(" (")[0][:34]} {p} x{r["per_device_qty"]}')
ALLOW = 9
def row(r_, item, unit=None, qty=None, notes="", url=None, total=True, bold=False, comment=None):
    c = wm.cell(r_, 1, item); c.font = BOLD if bold else BLK
    if url: c.hyperlink = url
    if comment: note(c, comment)
    if unit is not None:
        c = wm.cell(r_, 2, unit); c.number_format = USD; c.font = BLK if str(unit).startswith("=") else BLUE
    if qty is not None:
        c = wm.cell(r_, 3, qty); c.font = BLK if str(qty).startswith("=") else BLUE; c.alignment = Alignment(horizontal="center"); c.number_format = "0"
    if total and unit is not None and qty is not None:
        c = wm.cell(r_, 4, f"=B{r_}*C{r_}"); c.number_format = USD; c.font = BOLD if bold else BLK
    wm.cell(r_, 5, notes).font = F(color="595959"); wm.cell(r_, 5).alignment = Alignment(wrap_text=True, vertical="top")
row(R["starts"], "Board starts", qty=M["manufacturing"]["starts"], notes="30 accepted + 6 spare for yield")
row(R["acc"], "Accepted devices", qty=M["manufacturing"]["accepted_units"])
row(R["target"], "Target cost per device", unit=200)
S, A = f"$C${R['starts']}", f"$C${R['acc']}"
pcb, pcba, encl, strap, cable, pack, ship = (mfi("PCB"), mfi("PCBA"), mfi("Enclosure", "MJF"), mfi("Strap"), mfi("Charging"), mfi("Packaging"), mfi("Shipping/tariffs"))
row(R["pcb"], "PCB manufacturing (4-layer, JLCPCB)", pcb["unit_cost_usd"], f"={S}", "Derived, not quoted", pcb["source_url"])
row(R["pcba"], "Component placement + soldering (PCBA)", pcba["unit_cost_usd"], 1, "Setup, stencil, feeders, X-ray; not quoted", pcba["source_url"])
row(R["comp"], "Components per device", "=" + "+".join(terms) + f"+{ALLOW}", f"={S}", f"Core bare chips at qty-100 + ${ALLOW} passives allowance",
    comment="Qty-100 price x per-device qty (falls back to Actual, then Estimate):\n" + "\n".join(listing) + f"\nPassives/crystals/BLE antenna allowance: {ALLOW}")
row(R["encl"], "Enclosure (MJF nylon 2-part shell)", encl["unit_cost_usd"], f"={S}", "CNC aluminum would break the target", encl["source_url"])
row(R["band"], "Band / necklace", strap["unit_cost_usd"], f"={S}", "Cord with breakaway clasp", None)
row(R["cable"], "Charging cable (magnetic pogo)", cable["unit_cost_usd"], f"={S}", "$4.46 at 10+ (Adafruit)", cable["source_url"])
row(R["pack"], "Packaging", pack["unit_cost_usd"], f"={S}", "Box, foam, card")
row(R["ship"], "Shipping / tariffs", ship["unit_cost_usd"], 1, "JLCPCB DHL + US DDP tariff, DigiKey freight", ship["source_url"])
sim, fix, mag = mfi("SIM + data"), mfi("Test"), mfi("Magnet")
row(R["other"], "SIM + data plan, magnet, test fixture", f"=1*{S}+14*{A}+{mag['unit_cost_usd']}*{S}+{fix['unit_cost_usd']}", 1,
    "1NCE $1 SIM x starts + $14 plan x accepted; magnet; pogo jig",
    comment="Not in the requested row list but real costs from manufacturing.json: SIM $1 x 36, $14 flat plan x 30, magnet $1.50 x 36, test fixture $100.")
wm.cell(R["sub"], 1, "Subtotal").font = BLK
c = wm.cell(R["sub"], 4, f"=SUM(D{R['pcb']}:D{R['other']})"); c.number_format = USD; c.font = BLK
wm.cell(R["cont"], 1, "Contingency").font = BLK
c = wm.cell(R["cont"], 2, M["manufacturing"]["contingency_rate"]); c.number_format = "0%"; c.font = BLUE
c = wm.cell(R["cont"], 4, f"=B{R['cont']}*D{R['sub']}"); c.number_format = USD; c.font = BLK
wm.cell(R["cont"], 5, "Of subtotal").font = F(color="595959")
wm.cell(R["tot"], 1, "Total").font = BOLD
c = wm.cell(R["tot"], 4, f"=D{R['sub']}+D{R['cont']}"); c.number_format = USD; c.font = BOLD
wm.cell(R["per"], 1, "Cost per device").font = BOLD
c = wm.cell(R["per"], 4, f"=D{R['tot']}/{A}"); c.number_format = USD; c.font = BOLD
c = wm.cell(R["per"], 5, f'=IF(D{R["per"]}<=B{R["target"]},"✓ Under the $"&TEXT(B{R["target"]},"0")&" target","✗ Over the $"&TEXT(B{R["target"]},"0")&" target")')
c.font = BOLD; c.fill = SFILL
for r_ in (R["sub"], R["tot"], R["per"]):
    for j in range(1, 6): wm.cell(r_, j).border = TOP if r_ == R["tot"] else Border()
for j in range(1, 6): wm.cell(R["tot"], j).border = TOP
wm.freeze_panes = "A2"; wm.sheet_view.showGridLines = False
for w in (wc, wm):
    w.page_setup.orientation = "landscape"; w.page_setup.fitToWidth = 1; w.page_setup.fitToHeight = 0; w.sheet_properties.pageSetUpPr.fitToPage = True
wb.calculation.fullCalcOnLoad = True  # openpyxl writes no cached values
wb.save(OUT); print("saved", OUT, "| comp total cell B%d" % COMP_TOTAL)
