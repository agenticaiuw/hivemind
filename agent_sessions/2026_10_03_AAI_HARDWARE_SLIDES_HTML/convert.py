#!/usr/bin/env python3
"""Convert the unzipped PPTX in ./src into an editable HTML deck (deck.html + assets/).

Usage:  python3 convert.py            (run from anywhere; paths are relative to this file)

Geometry: the 12192000 x 6858000 EMU slide maps onto a 1920 x 1080 px canvas,
so 1 px = 6350 EMU and 1 pt = 2 px.

Handled: slide order from presentation.xml, layout/master placeholder inheritance
(xfrm, bodyPr, lstStyle), master txStyles + presentation defaultTextStyle, theme
colours/fonts with tint/shade/satMod/lumMod transforms, solid + linear gradient
backgrounds, rect/roundRect fills, pictures with srcRect crops, rotation, flips,
bullets (char / autonumber / none), spcBef, lnSpc, normAutofit fontScale +
lnSpcReduction, line breaks, bold/italic/underline/colour runs, online-video
posters (linked to the video).

Note: deck.html is regenerated from scratch by this script. Once you start
hand-editing deck.html, stop re-running the converter (or diff before overwriting).
"""
import colorsys
import html
import os
import re
import shutil
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
PPT = os.path.join(SRC, "ppt")
OUT_HTML = os.path.join(HERE, "deck.html")
ASSETS = os.path.join(HERE, "assets")

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}
R_EMBED = "{%s}embed" % NS["r"]
R_ID = "{%s}id" % NS["r"]
R_LINK = "{%s}link" % NS["r"]

EMU_PER_PX = 6350.0
LINE_FACTOR = 1.2  # PowerPoint single line height ~= 1.2 x font size for Aptos


def q(tag):
    pre, local = tag.split(":")
    return "{%s}%s" % (NS[pre], local)


def px(emu):
    return float(emu) / EMU_PER_PX


def fmt(v):
    """Short, readable px number."""
    v = round(v, 1)
    return str(int(v)) if v == int(v) else str(v)


def load(path):
    return ET.parse(path).getroot()


def rels_of(part_path):
    d, f = os.path.split(part_path)
    rp = os.path.join(d, "_rels", f + ".rels")
    out = {}
    if os.path.exists(rp):
        for rel in load(rp):
            out[rel.get("Id")] = (rel.get("Target"), rel.get("TargetMode"), rel.get("Type"))
    return out


def resolve(part_path, target):
    return os.path.normpath(os.path.join(os.path.dirname(part_path), target))


# --------------------------------------------------------------------------- theme
class Theme:
    def __init__(self, path):
        root = load(path)
        self.colors = {}
        cs = root.find(".//a:clrScheme", NS)
        for c in cs:
            name = c.tag.split("}")[1]
            child = c[0]
            val = child.get("lastClr") or child.get("val")
            self.colors[name] = val.upper()
        fs = root.find(".//a:fontScheme", NS)
        self.major = fs.find("a:majorFont/a:latin", NS).get("typeface")
        self.minor = fs.find("a:minorFont/a:latin", NS).get("typeface")


def clamp(x):
    return max(0.0, min(1.0, x))


def to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def from_lin(c):
    c = clamp(c)
    return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def apply_mods(hexv, mods):
    r, g, b = (int(hexv[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    alpha = 1.0
    for name, val in mods:
        v = val / 100000.0
        if name == "tint":  # towards white, in linear light
            r, g, b = (from_lin(to_lin(c) * v + (1 - v)) for c in (r, g, b))
        elif name == "shade":  # towards black, in linear light
            r, g, b = (from_lin(to_lin(c) * v) for c in (r, g, b))
        elif name in ("satMod", "lumMod", "lumOff"):
            h, l, s = colorsys.rgb_to_hls(r, g, b)
            if name == "satMod":
                s = clamp(s * v)
            elif name == "lumMod":
                l = clamp(l * v)
            else:
                l = clamp(l + v)
            r, g, b = colorsys.hls_to_rgb(h, l, s)
        elif name == "alpha":
            alpha = v
    rgb = "#%02X%02X%02X" % tuple(int(round(clamp(c) * 255)) for c in (r, g, b))
    if alpha < 1:
        return "rgba(%d,%d,%d,%.2f)" % (int(rgb[1:3], 16), int(rgb[3:5], 16), int(rgb[5:7], 16), alpha)
    return rgb


class Ctx:
    def __init__(self, theme, clrmap):
        self.theme = theme
        self.clrmap = clrmap

    def color(self, el):
        """el is a colour-choice element (srgbClr/schemeClr/sysClr) or a parent holding one."""
        if el is None:
            return None
        tag = el.tag.split("}")[1]
        if tag not in ("srgbClr", "schemeClr", "sysClr", "prstClr"):
            for c in el:
                v = self.color(c)
                if v:
                    return v
            return None
        if tag == "srgbClr":
            base = el.get("val")
        elif tag == "sysClr":
            base = el.get("lastClr")
        elif tag == "prstClr":
            base = {"black": "000000", "white": "FFFFFF"}.get(el.get("val"), "000000")
        else:
            name = el.get("val")
            name = self.clrmap.get(name, name)
            base = self.theme.colors.get(name, "000000")
        mods = [(m.tag.split("}")[1], int(m.get("val"))) for m in el]
        return apply_mods(base.upper(), mods)

    def fill(self, parent):
        """CSS background for a spPr/bgPr containing solidFill/gradFill/noFill."""
        if parent is None:
            return None
        sf = parent.find("a:solidFill", NS)
        if sf is not None:
            return self.color(sf)
        gf = parent.find("a:gradFill", NS)
        if gf is not None:
            stops = []
            for gs in gf.findall("a:gsLst/a:gs", NS):
                stops.append("%s %s%%" % (self.color(gs), fmt(int(gs.get("pos")) / 1000.0)))
            lin = gf.find("a:lin", NS)
            ang = int(lin.get("ang")) / 60000.0 if lin is not None else 90.0
            # DrawingML 0deg = left->right, clockwise; CSS 90deg = left->right.
            return "linear-gradient(%sdeg, %s)" % (fmt(ang + 90), ", ".join(stops))
        if parent.find("a:noFill", NS) is not None:
            return "transparent"
        return None

    def font(self, typeface):
        if typeface is None:
            return None
        if typeface.startswith("+mj"):
            return self.theme.major
        if typeface.startswith("+mn"):
            return self.theme.minor
        return typeface


# ------------------------------------------------------------------ text styles
PPR_ATTRS = ("marL", "indent", "algn")


def lvl_props(lst, lvl):
    """Extract paragraph+run defaults for level (1-based) from a list-style element."""
    out = {}
    if lst is None:
        return out
    el = lst.find("a:lvl%dpPr" % lvl, NS)
    if el is None:
        return out
    return ppr_props(el, el.find("a:defRPr", NS))


def ppr_props(ppr, rpr):
    out = {}
    if ppr is not None:
        for a in PPR_ATTRS:
            if ppr.get(a) is not None:
                out[a] = ppr.get(a)
        ln = ppr.find("a:lnSpc/a:spcPct", NS)
        if ln is not None:
            out["lnSpc"] = int(ln.get("val")) / 100000.0
        lnp = ppr.find("a:lnSpc/a:spcPts", NS)
        if lnp is not None:
            out["lnSpcPts"] = int(lnp.get("val")) / 100.0
        sb = ppr.find("a:spcBef/a:spcPts", NS)
        if sb is not None:
            out["spcBef"] = int(sb.get("val")) / 100.0
        sbp = ppr.find("a:spcBef/a:spcPct", NS)
        if sbp is not None:
            out["spcBefPct"] = int(sbp.get("val")) / 100000.0
        sa = ppr.find("a:spcAft/a:spcPts", NS)
        if sa is not None:
            out["spcAft"] = int(sa.get("val")) / 100.0
        if ppr.find("a:buNone", NS) is not None:
            out["bu"] = ("none", None)
        bc = ppr.find("a:buChar", NS)
        if bc is not None:
            out["bu"] = ("char", bc.get("char"))
        ba = ppr.find("a:buAutoNum", NS)
        if ba is not None:
            out["bu"] = ("num", ba.get("type"))
        bf = ppr.find("a:buFont", NS)
        if bf is not None:
            out["buFont"] = bf.get("typeface")
    out.update(rpr_props(rpr))
    return out


def rpr_props(rpr):
    out = {}
    if rpr is None:
        return out
    for a in ("sz", "b", "i", "u", "baseline"):
        if rpr.get(a) is not None:
            out[a] = rpr.get(a)
    sf = rpr.find("a:solidFill", NS)
    if sf is not None:
        out["color_el"] = sf
    lat = rpr.find("a:latin", NS)
    if lat is not None:
        out["latin"] = lat.get("typeface")
    return out


# ------------------------------------------------------------------- the parts
class Master:
    def __init__(self, path):
        self.path = path
        self.root = load(path)
        self.rels = rels_of(path)
        cm = self.root.find("p:clrMap", NS)
        self.clrmap = dict(cm.attrib)
        ts = self.root.find("p:txStyles", NS)
        self.title_style = ts.find("p:titleStyle", NS)
        self.body_style = ts.find("p:bodyStyle", NS)
        self.other_style = ts.find("p:otherStyle", NS)
        self.phs = collect_placeholders(self.root)
        self.bg = self.root.find("p:cSld/p:bg", NS)


class Layout:
    def __init__(self, path):
        self.path = path
        self.root = load(path)
        self.rels = rels_of(path)
        self.phs = collect_placeholders(self.root)
        self.bg = self.root.find("p:cSld/p:bg", NS)
        master_target = [t for t, _, ty in self.rels.values() if ty.endswith("/slideMaster")][0]
        self.master_path = resolve(path, master_target)


def ph_info(sp):
    ph = sp.find(".//p:nvPr/p:ph", NS)
    if ph is None:
        return None
    return {"type": ph.get("type") or "body", "idx": ph.get("idx"), "explicit_type": ph.get("type")}


def collect_placeholders(root):
    out = []
    for sp in root.find("p:cSld/p:spTree", NS):
        if sp.tag in (q("p:sp"), q("p:pic")):
            info = ph_info(sp)
            if info:
                out.append((info, sp))
    return out


def norm_type(t):
    return {"ctrTitle": "title", "subTitle": "body", "obj": "body"}.get(t, t)


def find_ph(phs, info):
    if info is None:
        return None
    # 1) exact idx match (titles have no idx)
    if info["idx"] is not None:
        for i, sp in phs:
            if i["idx"] == info["idx"]:
                return sp
    # 2) type match
    for i, sp in phs:
        if i["type"] == info["type"]:
            return sp
    for i, sp in phs:
        if norm_type(i["type"]) == norm_type(info["type"]):
            return sp
    return None


def xfrm_of(sp):
    x = sp.find("p:spPr/a:xfrm", NS)
    if x is None or x.find("a:off", NS) is None:
        return None
    off, ext = x.find("a:off", NS), x.find("a:ext", NS)
    return {
        "x": int(off.get("x")), "y": int(off.get("y")),
        "w": int(ext.get("cx")), "h": int(ext.get("cy")),
        "rot": int(x.get("rot", "0")) / 60000.0,
        "flipH": x.get("flipH") == "1", "flipV": x.get("flipV") == "1",
    }


# ------------------------------------------------------------------- rendering
class SlideRenderer:
    def __init__(self, theme, num, path, used_media):
        self.theme = theme
        self.num = num
        self.path = path
        self.root = load(path)
        self.rels = rels_of(path)
        lt = [t for t, _, ty in self.rels.values() if ty.endswith("/slideLayout")][0]
        self.layout = Layout(resolve(path, lt))
        self.master = Master(self.layout.master_path)
        self.ctx = Ctx(theme, self.master.clrmap)
        self.used_media = used_media
        self.pres_default = PRES_DEFAULT

    # ---- background
    def background(self):
        for owner in (self.root.find("p:cSld/p:bg", NS), self.layout.bg, self.master.bg):
            if owner is None:
                continue
            bgpr = owner.find("p:bgPr", NS)
            if bgpr is not None:
                return self.ctx.fill(bgpr)
            ref = owner.find("p:bgRef", NS)
            if ref is not None:
                return self.ctx.color(ref)
        return "#FFFFFF"

    # ---- title used for the comment header
    def title_text(self):
        for sp in self.root.iter(q("p:sp")):
            info = ph_info(sp)
            if info and info["type"] in ("title", "ctrTitle"):
                t = " ".join(" ".join((x.text or "") if x.tag == q("a:r") and x.find("a:t", NS) is None else
                                      ((x.find("a:t", NS).text or "") if x.tag == q("a:r") else " ")
                                      for x in p if x.tag in (q("a:r"), q("a:br"))) for p in sp.iter(q("a:p")))
                return re.sub(r"\s+", " ", t).strip()
        return ""

    def render(self):
        bg = self.background()
        title = self.title_text() or "Untitled"
        lines = []
        lines.append("<!-- Slide %d: %s -->" % (self.num, html.escape(title.replace("--", "-"))))
        style = "" if bg in ("#FFFFFF", None) else ' style="background: %s;"' % bg
        lines.append('<section class="slide" id="s%d"%s>' % (self.num, style))
        for el in self.root.find("p:cSld/p:spTree", NS):
            if el.tag == q("p:sp"):
                lines += self.render_sp(el)
            elif el.tag == q("p:pic"):
                lines += self.render_pic(el)
            elif el.tag in (q("p:grpSp"), q("p:graphicFrame"), q("p:cxnSp")):
                lines.append("  <!-- unsupported element %s skipped -->" % el.tag.split("}")[1])
        lines.append("</section>")
        return "\n".join(lines)

    # ---- inheritance helpers
    def inherited(self, sp):
        info = ph_info(sp)
        lay = find_ph(self.layout.phs, info) if info else None
        mas = None
        if info:
            # layouts reference master placeholders by type
            minfo = ph_info(lay) if lay is not None else info
            mas = find_ph(self.master.phs, {"type": minfo["type"], "idx": None, "explicit_type": None})
            if mas is None:
                mas = find_ph(self.master.phs, minfo)
        return info, lay, mas

    def geometry(self, sp, lay, mas):
        for s in (sp, lay, mas):
            if s is not None:
                x = xfrm_of(s)
                if x:
                    return x
        return None

    def box_style(self, g, extra=""):
        s = "left: %spx; top: %spx; width: %spx; height: %spx;" % (
            fmt(px(g["x"])), fmt(px(g["y"])), fmt(px(g["w"])), fmt(px(g["h"])))
        tr = []
        if g["rot"]:
            tr.append("rotate(%sdeg)" % fmt(g["rot"]))
        if g["flipH"]:
            tr.append("scaleX(-1)")
        if g["flipV"]:
            tr.append("scaleY(-1)")
        if tr:
            s += " transform: %s;" % " ".join(tr)
        return s + extra

    # ---- shapes
    def render_sp(self, sp):
        info, lay, mas = self.inherited(sp)
        if info and info["type"] in ("dt", "ftr", "sldNum"):
            return []  # slide-level footers are not shown unless placed on the slide
        g = self.geometry(sp, lay, mas)
        if g is None:
            return []
        sppr = sp.find("p:spPr", NS)
        css = []
        fill = self.ctx.fill(sppr)
        if sp.get("useBgFill") == "1":
            fill = self.background()
        if fill is None and info is None:
            style = sp.find("p:style", NS)
            if style is not None:
                fr = style.find("a:fillRef", NS)
                if fr is not None and fr.get("idx") not in ("0", None):
                    fill = self.ctx.color(fr)
        if fill and fill != "transparent":
            css.append("background: %s;" % fill)
        ln = sppr.find("a:ln", NS) if sppr is not None else None
        if ln is not None and ln.find("a:solidFill", NS) is not None:
            w = px(int(ln.get("w", "12700")))
            css.append("outline: %spx solid %s; outline-offset: -%spx;" % (
                fmt(w), self.ctx.color(ln.find("a:solidFill", NS)), fmt(w / 2)))
        geom = sppr.find("a:prstGeom", NS) if sppr is not None else None
        if geom is not None and geom.get("prst") == "roundRect":
            gd = geom.find("a:avLst/a:gd", NS)
            adj = int(gd.get("fmla").split()[1]) if gd is not None else 16667
            r = min(px(g["w"]), px(g["h"])) * adj / 100000.0
            css.append("border-radius: %spx;" % fmt(r))
        elif geom is not None and geom.get("prst") == "ellipse":
            css.append("border-radius: 50%;")

        body = self.text_html(sp, info, lay, mas)
        name = sp.find("p:nvSpPr/p:cNvPr", NS).get("name")
        has_text = body is not None
        if not has_text and not css:
            return []
        cls = "tx" if has_text else "shape"
        out = ['  <div class="%s" data-name="%s" style="%s">' % (
            cls, html.escape(name), self.box_style(g, (" " + " ".join(css)) if css else "") + (body[0] if has_text else ""))]
        if has_text:
            out += body[1]
        out.append("  </div>")
        if len(out) == 2:
            out = [out[0] + "</div>"]
        return out

    def text_html(self, sp, info, lay, mas):
        tb = sp.find("p:txBody", NS)
        if tb is None:
            return None
        paras = tb.findall("a:p", NS)
        if not any(p.find("a:r", NS) is not None or p.find("a:fld", NS) is not None for p in paras):
            return None
        # bodyPr: master -> layout -> slide
        bp = {}
        for s in (mas, lay, sp):
            if s is None:
                continue
            b = s.find("p:txBody/a:bodyPr", NS)
            if b is None:
                continue
            bp.update({k: v for k, v in b.attrib.items()})
            na = b.find("a:normAutofit", NS)
            if na is not None and s is sp:
                bp["fontScale"] = int(na.get("fontScale", "100000")) / 100000.0
                bp["lnSpcReduction"] = int(na.get("lnSpcReduction", "0")) / 100000.0
        ins = [px(int(bp.get(k, d))) for k, d in (("tIns", 45720), ("rIns", 91440), ("bIns", 45720), ("lIns", 91440))]
        anchor = bp.get("anchor", "t")
        fscale = bp.get("fontScale", 1.0)
        lnred = bp.get("lnSpcReduction", 0.0)

        # list-style chain, lowest priority first
        ptype = norm_type(info["type"]) if info else None
        if ptype == "title":
            base = self.master.title_style
        elif ptype is not None:
            base = self.master.body_style
        else:
            base = None  # text boxes: presentation defaults + master otherStyle
        chain = []
        if base is None:
            chain += [self.pres_default, self.master.other_style]
        else:
            chain.append(base)
        for s in (mas, lay, sp):
            if s is not None:
                chain.append(s.find("p:txBody/a:lstStyle", NS))

        style_bits = []
        if ins != [7.2, 14.4, 7.2, 14.4]:
            style_bits.append(" padding: %s;" % " ".join("%spx" % fmt(v) for v in ins))
        if anchor == "ctr":
            style_bits.append(" justify-content: center;")
        elif anchor == "b":
            style_bits.append(" justify-content: flex-end;")
        if fscale != 1.0:
            style_bits.append(" /* autofit: fontScale %s */" % fscale)

        out_lines = []
        num_counter = 0
        for pi, p in enumerate(paras):
            ppr = p.find("a:pPr", NS)
            lvl = int(ppr.get("lvl", "0")) + 1 if ppr is not None else 1
            props = {}
            for lst in chain:
                props.update(lvl_props(lst, lvl))
            props.update(ppr_props(ppr, None))
            if props.get("bu", ("none",))[0] == "num":
                num_counter += 1
            else:
                num_counter = 0
            out_lines.append(self.para_html(p, props, fscale, lnred, num_counter, pi == 0))
        # hoist the most common font-size / line-height / paragraph gap to the box
        def common(prefix, items):
            vals = [next((c for c in css if c.startswith(prefix)), None) for css in items]
            vals = [v for v in vals if v]
            return max(set(vals), key=vals.count) if vals else None
        box = []
        fs = common("font-size:", [o[2] for o in out_lines if "<br>" != o[3]] or [o[2] for o in out_lines])
        lh = common("line-height:", [o[2] for o in out_lines])
        gap = common("margin-top:", [o[2] for o in out_lines[1:]])
        for d in (fs, lh):
            if d:
                box.append(d)
        if gap:
            box.append("--gap: %s" % gap.split(":", 1)[1].strip())
        lines = []
        for i, (cls, attrs, css, body) in enumerate(out_lines):
            css = [c for c in css if c not in (fs, lh) and not (gap and c == gap)]
            if gap and i > 0 and not any(c.startswith("margin-top:") for c in css) and \
                    out_lines[i][2] is not None and not any(c.startswith("margin-top:") for c in out_lines[i][2]):
                css.append("margin-top: 0;")
            cls_attr = ' class="%s"' % " ".join(cls) if cls else ""
            st = ' style="%s"' % " ".join(css) if css else ""
            lines.append("    <p%s%s%s>%s</p>" % (cls_attr, attrs, st, body))
        return " " + " ".join(box) + "".join(style_bits), lines

    def run_css(self, rp, base, fscale):
        """CSS for a run relative to the paragraph defaults `base`."""
        bits = []
        if rp.get("sz") and rp.get("sz") != base.get("sz"):
            bits.append("font-size: %spx;" % fmt(int(rp["sz"]) / 100.0 * 2 * fscale))
        if rp.get("b") is not None and rp.get("b") != base.get("b"):
            bits.append("font-weight: %s;" % ("bold" if rp["b"] == "1" else "normal"))
        if rp.get("i") is not None and rp.get("i") != base.get("i"):
            bits.append("font-style: %s;" % ("italic" if rp["i"] == "1" else "normal"))
        if rp.get("u") and rp.get("u") != "none":
            bits.append("text-decoration: underline;")
        if "color_el" in rp:
            c = self.ctx.color(rp["color_el"])
            bc = self.ctx.color(base["color_el"]) if "color_el" in base else None
            if c != bc:
                bits.append("color: %s;" % c)
        if rp.get("latin"):
            f = self.ctx.font(rp["latin"])
            if f != self.ctx.font(base.get("latin")):
                bits.append("font-family: %s;" % font_stack(f))
        return " ".join(bits)

    def para_html(self, p, props, fscale, lnred, num, first):
        # hoist a run size shared by every run up to the paragraph (cleaner markup,
        # and PowerPoint sizes the bullet from the first run anyway)
        run_szs = {(r.find("a:rPr", NS).get("sz") if r.find("a:rPr", NS) is not None else None)
                   for r in p.findall("a:r", NS)}
        if len(run_szs) == 1 and None not in run_szs:
            props = dict(props, sz=run_szs.pop())
        sz =int(props.get("sz", "1800")) / 100.0 * 2 * fscale  # px
        css = ["font-size: %spx;" % fmt(sz)]
        fam = self.ctx.font(props.get("latin", "+mn-lt"))
        if fam == self.theme.major:
            cls = ["mj"]
        else:
            cls = []
            if fam != self.theme.minor:
                css.append("font-family: %s;" % font_stack(fam))
        if "color_el" in props:
            c = self.ctx.color(props["color_el"])
            if c != "#000000":
                css.append("color: %s;" % c)
        if props.get("b") == "1":
            css.append("font-weight: bold;")
        if props.get("i") == "1":
            css.append("font-style: italic;")
        algn = props.get("algn", "l")
        if algn != "l":
            css.append("text-align: %s;" % {"ctr": "center", "r": "right", "just": "justify"}.get(algn, "left"))
        if "lnSpcPts" in props:
            css.append("line-height: %spx;" % fmt(props["lnSpcPts"] * 2))
        else:
            ls = max(props.get("lnSpc", 1.0) - lnred, 0.1)
            css.append("line-height: %s;" % round(ls * LINE_FACTOR, 3))
        if not first:
            if "spcBef" in props and props["spcBef"]:
                css.append("margin-top: %spx;" % fmt(props["spcBef"] * 2 * fscale))
            elif props.get("spcBefPct"):
                css.append("margin-top: %spx;" % fmt(props["spcBefPct"] * sz * LINE_FACTOR))
        if props.get("spcAft"):
            css.append("margin-bottom: %spx;" % fmt(props["spcAft"] * 2 * fscale))
        marl = px(int(props.get("marL", "0")))
        ind = px(int(props.get("indent", "0")))
        if marl:
            css.append("padding-left: %spx;" % fmt(marl))
        if ind:
            css.append("text-indent: %spx;" % fmt(ind))

        bu = props.get("bu", ("none", None))
        runs = p.findall("*")
        has_text = any(r.tag in (q("a:r"), q("a:fld")) for r in runs)
        attrs = ""
        if has_text and bu[0] == "char":
            cls.append("bu")
            if bu[1] != "•":
                attrs = ' data-bu="%s"' % html.escape(bu[1])
        elif has_text and bu[0] == "num":
            cls.append("num")
            bfont = self.ctx.font(props.get("buFont"))
            if bfont == self.theme.major:
                cls.append("num-mj")
            attrs = ' data-n="%d"' % num
        if has_text and bu[0] in ("char", "num") and ind < 0:
            css.append("--hang: %spx;" % fmt(-ind))

        inner = []
        for r in runs:
            if r.tag in (q("a:r"), q("a:fld")):
                rp = dict(props)
                rp_own = rpr_props(r.find("a:rPr", NS))
                rp.update(rp_own)
                text = html.escape((r.find("a:t", NS).text or ""))
                rc = self.run_css(rp_own, props, fscale)
                inner.append('<span style="%s">%s</span>' % (rc, text) if rc else text)
            elif r.tag == q("a:br"):
                inner.append("<br>")
        if not has_text:
            end = p.find("a:endParaRPr", NS)
            if end is not None and end.get("sz"):
                css[0] = "font-size: %spx;" % fmt(int(end.get("sz")) / 100.0 * 2 * fscale)
            inner = ["<br>"]
        # a single span wrapping the whole paragraph: hoist its style onto the <p>
        body = "".join(inner)
        m = re.fullmatch(r'<span style="([^"]*)">(.*)</span>', body)
        if m and "<span" not in m.group(2):
            body = m.group(2)
            css += [b.strip() + ";" for b in m.group(1).split(";") if b.strip()]
        if has_text and bu[0] in ("char", "num"):
            # .bu/.num default to the master's level-1 hang (36px); drop if equal
            for d in ("padding-left: 36px;", "text-indent: -36px;", "--hang: 36px;"):
                if d in css:
                    css.remove(d)
        return cls, attrs, css, body

    # ---- pictures
    def render_pic(self, pic):
        info, lay, mas = self.inherited(pic)
        g = self.geometry(pic, lay, mas)
        blip = pic.find("p:blipFill/a:blip", NS)
        target = self.rels[blip.get(R_EMBED)][0]
        media = resolve(self.path, target)
        fname = os.path.basename(media)
        self.used_media.add(media)
        cnv = pic.find("p:nvPicPr/p:cNvPr", NS)
        alt = html.escape(cnv.get("descr") or cnv.get("name") or "", quote=True)
        src = "assets/" + fname
        link = None
        vf = pic.find("p:nvPicPr/p:nvPr/a:videoFile", NS)
        if vf is not None and vf.get(R_LINK) in self.rels:
            link = self.rels[vf.get(R_LINK)][0]
            m = re.search(r"youtube\.com/embed/([\w-]+)", link)
            if m:
                link = "https://www.youtube.com/watch?v=" + m.group(1)
        sr = pic.find("p:blipFill/a:srcRect", NS)
        crop = {k: int(sr.get(k, "0")) / 100000.0 for k in "ltrb"} if sr is not None else None
        if crop and not any(crop.values()):
            crop = None
        out = []
        if crop:
            vw = 1 - crop["l"] - crop["r"]
            vh = 1 - crop["t"] - crop["b"]
            inner = 'style="width: %s%%; height: %s%%; left: %s%%; top: %s%%;"' % (
                fmt(100 / vw), fmt(100 / vh), fmt(-100 * crop["l"] / vw), fmt(-100 * crop["t"] / vh))
            out.append('  <div class="pic crop" style="%s">' % self.box_style(g))
            out.append('    <img src="%s" alt="%s" %s>' % (src, alt, inner))
            out.append("  </div>")
        else:
            out.append('  <img class="pic" src="%s" alt="%s" style="%s">' % (src, alt, self.box_style(g)))
        if link:
            first = out[0].lstrip()
            out = ['  <a class="media" href="%s" target="_blank" rel="noopener" title="Play video">' % html.escape(link)] + \
                ["  " + l for l in out] + ["  </a>"]
        return out


def font_stack(name):
    return '"%s", Aptos, "Segoe UI", "Helvetica Neue", Arial, sans-serif' % name


PRES_DEFAULT = None


def main():
    global PRES_DEFAULT
    pres_path = os.path.join(PPT, "presentation.xml")
    pres = load(pres_path)
    PRES_DEFAULT = pres.find("p:defaultTextStyle", NS)
    prels = rels_of(pres_path)
    theme_target = [t for t, _, ty in prels.values() if ty.endswith("/theme")][0]
    theme = Theme(resolve(pres_path, theme_target))
    slide_paths = [resolve(pres_path, prels[s.get(R_ID)][0]) for s in pres.find("p:sldIdLst", NS)]

    used = set()
    sections = []
    for i, sp in enumerate(slide_paths, 1):
        sections.append(SlideRenderer(theme, i, sp, used).render())

    os.makedirs(ASSETS, exist_ok=True)
    for m in sorted(used):
        shutil.copy2(m, os.path.join(ASSETS, os.path.basename(m)))

    with open(os.path.join(HERE, "deck_template.html"), encoding="utf-8") as f:
        tpl = f.read()
    doc = tpl.replace("{{MAJOR}}", theme.major).replace("{{MINOR}}", theme.minor) \
        .replace("{{SLIDES}}", "\n\n".join(sections))
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(doc)
    print("wrote %s (%d slides, %d media files)" % (OUT_HTML, len(sections), len(used)))


if __name__ == "__main__":
    main()
