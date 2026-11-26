"""STAMPKEEPER - the Sunsoft tag travels from the old CV to the new one.
Rules in notes/WORKFLOW.md s.2, 2b, 2c, 8. Orders: tag first, then decide about the move.
"""
import os, shutil
import pdfplumber
from pypdf.generic import RectangleObject, ArrayObject, NameObject, NumberObject  # MOVE-STAMP v85.267
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import FreeText
from pypdf.generic import NameObject, TextStringObject

STAMP_STYLE = {'font': 'Helvetica-Bold', 'font_size': round(24.0 * 0.483003917, 5), 'line_pt': 14.0, 'colour': 'FF0000', 'editor_factor': 0.483003917, 'editor_points': 24.0, 'da_ratio': round(1.0 / 0.483003917, 6), 'editor_inset': 1.119, 'bleed_pt': 0.5}  # SIZE-24 v85.285: the master's Preview setting - Helvetica 24pt bold red left, never 12  # NO-LITERALS v85.264: the house defaults, declared once  # SIZE-HOUSE v85.360  # DA-COUNTER v85.368  # STAMP-TRUTH-2 v85.374  # EDITOR-FACTOR v85.378  # STAMP-24-EXACT v85.379  # SAME-TO-SAME v85.380  # SAME-TO-SAME v85.380-ratio  # PIXEL-SAME v85.381  # NO-CLIP v85.382-ratio  # INK-FIT v85.384
STAMP_PLACEMENT = {'dpi': 120, 'ink': 128, 'page_margin': 30.0, 'band_pad': 6.0}  # NO-LITERALS v85.264: the placement numbers, declared once
RED = 'FF0000'
LINE_H = 14.5
PAD = 8
MARGIN = 16
HOLD_FOLDERS = ('Closed \u2013 Not Proceeding', 'Closed - Not Proceeding')
READY = 'Ready for Manager Review'


def stamp_from(pdf):
    """the first FreeText annotation that is a COMPLETE Sunsoft stamp, or None"""
    import butler
    try:
        r = PdfReader(pdf)
    except Exception:
        return None
    for pno, pg in enumerate(r.pages):
        a = pg.get('/Annots')
        if a is None:
            continue
        for ref in a.get_object():
            o = ref.get_object()
            if str(o.get('/Subtype')) != '/FreeText':
                continue
            txt = str(o.get('/Contents') or '')
            ok, miss = butler.stamp_complete(txt)
            if not ok:
                continue
            rect = [float(v) for v in o.get('/Rect')]
            import re as _re  # NO-LITERALS v85.264: the appearance is parsed, never assumed
            _da = str(o.get('/DA') or '')
            _sz = STAMP_STYLE['font_size']; _fn = STAMP_STYLE['font']; _co = STAMP_STYLE['colour']
            _m = _re.search(r'([0-9.]+)[ ]+Tf', _da)
            if _m:
                try: _sz = da_drawn(_da)  # DA-COUNTER v85.368
                except Exception: pass
            _mf = _re.search(r'/([A-Za-z0-9.-]+)[ ]+[0-9.]+[ ]+Tf', _da)
            if _mf: _fn = _mf.group(1)
            _mc = _re.search(r'([0-9.]+)[ ]+([0-9.]+)[ ]+([0-9.]+)[ ]+rg', _da)
            if _mc:
                _co = '%02X%02X%02X' % tuple(int(round(float(v) * 255)) for v in _mc.groups())
            return {'text': txt, 'w': rect[2] - rect[0], 'h': rect[3] - rect[1], 'page': pno + 1,
                    'size': _sz, 'font': _fn, 'colour': _co}
    return None


def da_ratio():  # DA-COUNTER v85.368: the ONE place the editors factor lives - Preview rewrites a FreeText appearance at 0.483031 x /DA
    return float(STAMP_STYLE.get('da_ratio') or 1.0)


def da_size(size):  # DA-COUNTER v85.368: the number /DA must carry so the editor renders the drawn size
    return round(float(size) * da_ratio(), 2)  # SAME-TO-SAME v85.380


def da_drawn(da):  # DA-COUNTER v85.368: the DRAWN size behind a /DA string - every reader divides once, never guesses
    import re as _re
    _m = _re.search(r"/([A-Za-z0-9.+-]+)[ ]+([0-9.]+)[ ]+Tf", str(da or ""))
    if not _m:
        return 0.0
    return float(_m.group(2)) / (da_ratio() or 1.0)


def ink_extents(text):  # INK-FIT v85.384: what the glyphs actually occupy - width, ink above the first baseline, ink below the last
    _lines = [l for l in str(text).split(chr(10)) if l.strip()]
    _sz = float(STAMP_STYLE['font_size'])
    try:
        from PIL import ImageFont as _IF
        _f = _IF.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', max(1, int(round(_sz * 10))))
        _asc, _desc = _f.getmetrics()
        _w = 0.0
        _above = 0.0  # INK-FIT v85.384
        _below = _desc / 10.0
        for _l in _lines:
            _b = _f.getbbox(_l)
            if not _b:
                continue
            _w = max(_w, _b[2] / 10.0)
            _above = max(_above, (_asc - _b[1]) / 10.0)
            _below = max(_below, (_b[3] - _asc) / 10.0)
        return (_w, _above, _below)
    except Exception:
        return (0.0, _sz, _sz * 0.25)


def need_size(text, src_w=None, src_h=None):  # MEASURE-TEXT v85.283: the box comes from the REAL glyph widths at the signature size (a per-character guess made it ~20% too wide)
 lines = [l for l in str(text).split(chr(10)) if l.strip()]
 size = float(STAMP_STYLE['font_size'])
 w = 0.0
 try:
     from PIL import ImageFont as _IF
     _f = _IF.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', max(1, int(round(float(STAMP_STYLE['font_size']) * 10))))  # AUTO-FIT v85.286: metrics at the apparent size  # BOX-FIT v85.355  # NO-CLIP v85.382
     w = ink_extents(str(text))[0] + 2.0 * float(STAMP_STYLE.get('bleed_pt') or 0.5)  # NO-CLIP v85.382  # INK-FIT v85.384
 except Exception:
     w = max((len(l) for l in lines), default=0) * 6.9
 pass  # INK-FIT v85.384: the old +4 pad and 80pt floor are gone - the frame is the ink plus one bleed   # AP-OWN v85.357  # AP-OWN v85.357  # INK-FIT v85.384
 h = ink_extents(str(text))[1] + (max(1, len(lines)) - 1) * float(STAMP_STYLE.get('line_pt') or 14.6) + ink_extents(str(text))[2] + 2.0 * float(STAMP_STYLE.get('bleed_pt') or 0.5)   # AP-OWN v85.357: the box is exactly the drawing  # AUTO-FIT v85.286  # PITCH-SIZE v85.345  # AP-OWN v85.357  # EDIT-FIT v85.364  # V-FIT v85.383  # INK-FIT v85.384
 return w, h
def best_spot(pdf, w, h, page=None):  # OPEN-STAMP v85.350
    """end of the CV first; title strip clear; least overlap; then lowest and leftmost"""
    with pdfplumber.open(pdf) as doc:
        n = len(doc.pages)
        order = list(range(n - 1, -1, -1))
        if n >= 2:
            lp = doc.pages[-1]
            lw = lp.extract_words()
            lb = max([float(x['bottom']) for x in lw], default=0)
            if len(lw) < 40 or lb < float(lp.height) * 0.55:
                order = list(range(n - 2, -1, -1)) + [n - 1]
        # BELOW-FIRST v85.245: pass 1 tries the master's geometry on EVERY page in order before any
        # free-space search - otherwise a page's fallback wins and the aligned placement never happens.
        if page:                                          # OPEN-STAMP v85.350: the masters page wins
            try:
                _p0 = int(page) - 1
                if 0 <= _p0 < n:
                    order = [_p0]
            except Exception:
                pass
        for pno in order:
            pg = doc.pages[pno]
            W, H = float(pg.width), float(pg.height)
            if w > W - 2 * MARGIN or h > H - 2 * MARGIN:
                continue
            _ws = pg.extract_words()
            if not _ws:
                continue
            _lastb = max(float(x['bottom']) for x in _ws)
            _leftc = max(20.0, min(min(float(x['x0']) for x in _ws), W / 2))
            _top = (H - _lastb) - 13
            if _top - h >= 18 and _leftc + w <= W - 20:
                return pno, (_leftc, _top - h, _leftc + w, _top), 0
        for pno in order:
            pg = doc.pages[pno]
            W, H = float(pg.width), float(pg.height)
            words = [(float(x['x0']), float(x['top']), float(x['x1']), float(x['bottom'])) for x in pg.extract_words()]
            if not words and page:
                return pno, (MARGIN + 20, MARGIN + 20, MARGIN + 20 + w, MARGIN + 20 + h), 0
            if not words or w > W - 2 * MARGIN or h > H - 2 * MARGIN:  # OPEN-STAMP v85.350
                continue
            # BELOW-TEXT v85.245: the master's own geometry - aligned to the text's left edge, 13pt under the
            # last line, >=18pt of air below the tag. Only when that does not fit do we search free space.
            _lastb = max(float(x['bottom']) for x in pg.extract_words())
            _left = min(float(x['x0']) for x in pg.extract_words())
            _LEFTC = max(20.0, min(_left, W / 2))
            _top_pdf = (H - _lastb) - 13
            if _top_pdf - h >= 18 and _LEFTC + w <= W - 20:
                _box = (_LEFTC, _top_pdf - h, _LEFTC + w, _top_pdf)
                _ov = 0.0
                for wd in words:
                    if _box[2] <= wd[0] or _box[0] >= wd[2] or _box[3] <= wd[1] or _box[1] >= wd[3]:
                        continue
                    _ov += (min(_box[2], wd[2]) - max(_box[0], wd[0])) * (min(_box[3], wd[3]) - max(_box[1], wd[1]))
                if _ov == 0:
                    return pno, _box, 0
            page_best = None
            for top in range(int(H - MARGIN - h), int(MARGIN) - 1, -8):
                for x in range(int(MARGIN), int(W - MARGIN - w) + 1, 8):
                    box = (x, top, x + w, top + h)
                    head = (x, top, x + w, top + 16)
                    ov = 0.0
                    head_ov = 0
                    for wd in words:
                        if box[2] <= wd[0] or box[0] >= wd[2] or box[3] <= wd[1] or box[1] >= wd[3]:
                            continue
                        ov += (min(box[2], wd[2]) - max(box[0], wd[0])) * (min(box[3], wd[3]) - max(box[1], wd[1]))
                        if not (head[2] <= wd[0] or head[0] >= wd[2] or head[3] <= wd[1] or head[1] >= wd[3]):
                            head_ov += 1
                    score = (head_ov > 0, ov, top + h, x)
                    if page_best is None or score < page_best[0]:
                        page_best = (score, box, ov, H)
            if page_best is None:
                if page_best[2] > 0:  # BOTTOM-ONLY v85.261: an overlapping spot is NOT a spot - keep looking (Akshat Utreja overlap 467 was this path)
                    continue
                continue
            box = page_best[1]
            return pno, (box[0], page_best[3] - box[3], box[2], page_best[3] - box[1]), page_best[2]
    return None, None, None


def best_spot_ink(pdf, w, hgt):  # INK-SPOT v85.262: the blank space is measured in INK - a scanned CV has no text layer to trust
    import pdfplumber as _pl
    try:
        with _pl.open(pdf) as doc:
            for pno in range(len(doc.pages) - 1, -1, -1):
                page = doc.pages[pno]
                W, H = float(page.width), float(page.height)
                if w > W - 40 or hgt > H - 40:
                    continue
                img = page.to_image(resolution=120).original.convert(chr(76))
                pw, ph = img.size
                sx, sy = pw / W, ph / H
                px = img.load()
                rows = [sum(1 for x in range(0, pw, 2) if px[x, y] < 128) > 1 for y in range(ph)]
                need = int((hgt + 6) * sy)  # INK-SPOT: a band just tall enough qualifies
                band = None
                y_end = ph - 1
                while y_end > need:
                    if not rows[y_end]:
                        y_top = y_end
                        while y_top >= 0 and not rows[y_top]:
                            y_top -= 1
                        if (y_end - y_top) >= need:
                            band = (y_top + 1, y_end); break
                        y_end = y_top
                    else:
                        y_end -= 1
                if band is None:
                    continue
                try:
                    ws = page.extract_words()
                    left = min((float(x['x0']) for x in ws), default=0) if ws else 0
                except Exception:
                    left = 0
                if not left:
                    for x in range(pw):
                        if any(px[x, y] < 128 for y in range(0, ph, 3)):
                            left = x / sx; break
                x0 = max(10.0, float(left))
                bw = min(w, W - x0 - 10)
                top = band[0] / sy + 4.0  # INK-SPOT: just BELOW the text above, never at the foot of the page
                if top + hgt > H - 30:
                    continue  # INK-SPOT: a >=30 pt page-edge margin is mandatory
                bx0, by0 = int(x0 * sx), int(top * sy)
                bx1, by1 = int((x0 + bw) * sx), int((top + hgt) * sy)
                dark = sum(1 for x in range(max(0, bx0), min(pw, bx1)) for y in range(max(0, by0), min(ph, by1)) if px[x, y] < 128)
                if dark == 0:
                    return pno, (x0, H - (top + hgt), x0 + bw, H - top), 0
        return None, None, None
    except Exception:
        return None, None, None


def has_stamp(pdf):
    """any FreeText annotation at all (complete or not)"""
    try:
        r = PdfReader(pdf)
    except Exception:
        return False
    for pg in r.pages:
        a = pg.get('/Annots')
        if a is None:
            continue
        for ref in a.get_object():
            if str(ref.get_object().get('/Subtype')) == '/FreeText':
                return True
    return False


def has_complete_stamp(pdf):  # STAMP-TRUTH v85.345: a stamp counts only when every field is readable
    return stamp_from(pdf) is not None


def stamp_verify(pdf):  # STAMP-VERIFY v85.348: one stamp, bold, the masters size, face declared, complete
    import re as _re
    out = {"ok": False, "why": "unreadable"}
    try:
        r = PdfReader(pdf)
    except Exception:
        return out
    declared = set()
    try:
        _acro = r.trailer["/Root"].get("/AcroForm") or {}
        _dr = _acro.get("/DR") or {}
        for _k in (_dr.get("/Font") or {}):
            declared.add(str(_k).lstrip("/"))
    except Exception:
        declared = set()
    recs = []
    for _pno, _pg in enumerate(r.pages):
        for _ref in (_pg.get("/Annots") or []):
            _o = _ref.get_object()
            if str(_o.get("/Subtype")) != "/FreeText":
                continue
            _t = str(_o.get("/Contents") or "")
            if "Sunsoft" not in _t:
                continue
            recs.append((_pno, [float(v) for v in _o.get("/Rect")], str(_o.get("/DA") or ""), _t, _o.get("/AP")))  # AP-REQUIRE v85.358
    if not recs:
        return {"ok": False, "why": "no stamp"}
    if len(recs) > 1:
        return {"ok": False, "why": "stacked (%d stamps)" % len(recs)}
    _pno, _rect, _da, _txt, _ap = recs[0]  # AP-REQUIRE v85.358
    _m = _re.search(r"/([A-Za-z0-9.+-]+)[ ]+([0-9.]+)[ ]+Tf", _da)
    if not _m:
        return {"ok": False, "why": "no /DA - the viewer picks the face (not bold)"}
    _font, _size = _m.group(1), da_drawn(_da)  # DA-COUNTER v85.368
    if "bold" not in _font.lower():
        return {"ok": False, "why": "not bold (%s)" % _font}
    if abs(_size - float(STAMP_STYLE["font_size"])) > 0.25:  # STAMP-24-EXACT v85.379
        return {"ok": False, "why": "size %g, not %g" % (_size, float(STAMP_STYLE["font_size"]))}
    try:                                 # BOX-FIT v85.355: a squeezed frame is not a good stamp
        _nw, _nh = need_size(_txt)
        if (_rect[2] - _rect[0]) < 0.95 * _nw:
            return {"ok": False, "why": "frame too narrow (%d of %d) - the text is squeezed" % (int(_rect[2] - _rect[0]), int(_nw))}
    except Exception:
        pass
    try:                                  # STAMP-TRUTH-2 v85.374: the DRAWN size is the truth - /DA alone cannot prove a stamp was not resized
        _n0 = _ap.get_object().get("/N") if _ap else None
        _n0 = _n0.get_object() if hasattr(_n0, "get_object") else _n0
        _dr = [float(v) for v in _re.findall(r"/TT1 ([0-9.]+) Tf", _n0.get_data().decode("latin-1", "ignore"))]
        if _dr and abs(_dr[0] - float(STAMP_STYLE["font_size"])) > 0.5:
            return {"ok": False, "why": "drawn %g, not %g - the stamp was resized" % (_dr[0], float(STAMP_STYLE["font_size"]))}
    except Exception:
        pass
    if not _ap:                                  # AP-REQUIRE v85.358: without our drawing the viewer picks a size
        return {"ok": False, "why": "no drawn appearance - the viewer would pick its own size"}
    try:
        _nb = _ap.get_object().get("/N")
        _nb = _nb.get_object() if hasattr(_nb, "get_object") else _nb
        _bb = [float(v) for v in _nb["/BBox"]]
        if abs((_bb[2] - _bb[0]) - (_rect[2] - _rect[0])) > 1.5 or abs((_bb[3] - _bb[1]) - (_rect[3] - _rect[1])) > 1.5:
            return {"ok": False, "why": "the drawing does not fill the frame"}
    except Exception:
        pass
    try:                                 # PITCH-CHECK v85.365: a tight box makes Preview shrink the text on edit
        _nl = len([l for l in str(_txt).split(chr(10)) if l.strip()])
        _np = float(_rect[3] - _rect[1]) / max(1, _nl)
        if (_rect[3] - _rect[1]) < ink_extents(_txt)[1] + (_nl - 1) * float(STAMP_STYLE.get('line_pt') or 14.6) + ink_extents(_txt)[2] - 0.5:  # INK-FIT v85.384
            return {"ok": False, "why": "box too tight (%.1f pt per line) - Preview would shrink the text on edit" % _np}
    except Exception:
        pass
    if _font not in declared:
        return {"ok": False, "why": "face /%s not declared in the form" % _font}
    try:
        import butler as _b
        _c, _miss = _b.stamp_complete(_txt)
        if not _c:
            return {"ok": False, "why": "incomplete (%s)" % ", ".join(_miss[:3])}
    except Exception:
        pass
    return {"ok": True, "why": "one bold %gpt stamp, face declared" % _size}


def stamp_health(pdf):  # STAMP-HEALTH v85.345: how many stamps, at what size, and are all fields readable
    import re as _re
    out = {"n": 0, "size": None, "complete": False}
    try:
        r = PdfReader(pdf)
    except Exception:
        return out
    try:
        import butler as _b
    except Exception:
        _b = None
    for pg in r.pages:
        a = pg.get("/Annots")
        if a is None:
            continue
        for ref in a.get_object():
            o = ref.get_object()
            if str(o.get("/Subtype")) != "/FreeText":
                continue
            txt = str(o.get("/Contents") or "")
            if "Sunsoft" not in txt:
                continue
            out["n"] += 1
            if out["size"] is None:
                m = _re.search(r"([0-9.]+) Tf", str(o.get("/DA") or ""))
                if m:
                    try: out["size"] = da_drawn(str(o.get("/DA") or ""))  # DA-COUNTER v85.368
                    except Exception: pass
            if _b is not None:
                try:
                    if _b.stamp_complete(txt)[0]: out["complete"] = True
                except Exception: pass
    return out


def any_stamp_text(pdf):
    """the FIRST FreeText text even when incomplete - carried, then held"""
    try:
        r = PdfReader(pdf)
    except Exception:
        return None
    for pg in r.pages:
        a = pg.get('/Annots')
        if a is None:
            continue
        for ref in a.get_object():
            o = ref.get_object()
            if str(o.get('/Subtype')) == '/FreeText':
                t = str(o.get('/Contents') or '').strip()
                if t and t.lower() != 'none':
                    return t
    return None


def _ensure_stamp_font(wr):  # FONT-RES v85.288: a /DA font name only works when the AcroForm declares it - otherwise viewers substitute a plain face
    from pypdf.generic import DictionaryObject as _D, NameObject as _N
    try:
        _root = wr._root_object
        _ac = _root.get('/AcroForm')
        if _ac is None:
            _ac = _D(); _root[_N('/AcroForm')] = _ac
        _dr = _ac.get('/DR')
        if _dr is None:
            _dr = _D(); _ac[_N('/DR')] = _dr
        _fonts = _dr.get('/Font')
        if _fonts is None:
            _fonts = _D(); _dr[_N('/Font')] = _fonts
        _key = _N('/Helvetica-Bold')
        if _key not in _fonts:
            _fonts[_key] = _D({_N('/Type'): _N('/Font'), _N('/Subtype'): _N('/Type1'),
                               _N('/BaseFont'): _N('/Helvetica-Bold'), _N('/Encoding'): _N('/WinAnsiEncoding')})
        return True
    except Exception:
        return False


def _draw_ap(wr, annot, text, w, h, size, colour="FF0000"):  # AP-OWN v85.357: the appearance is ours, at our size
    try:
        from pypdf.generic import DictionaryObject, DecodedStreamObject, FloatObject
        _lines = [l for l in str(text).split(chr(10)) if l.strip()]
        _sz = float(size)
        _lead = float(STAMP_STYLE.get('line_pt') or 14.6)   # SIZE-HOUSE v85.360: the drawing follows the frame  # SIZE-HOUSE v85.360  # V-FIT v85.383
        _esc = lambda s: s.replace(chr(92), chr(92) * 2).replace("(", chr(92) + "(").replace(")", chr(92) + ")")
        _rgb = "1 0 0 rg"
        try:
            _rgb = "%g %g %g rg" % tuple(int(str(colour)[k:k + 2], 16) / 255.0 for k in (0, 2, 4))
        except Exception:
            pass
        _parts = ["q", _rgb, "BT", "/TT1 %g Tf" % _sz]
        _y = float(h) - float(STAMP_STYLE.get('bleed_pt') or 0.5) - ink_extents(str(text))[1]  # PIXEL-SAME v85.381  # INK-FIT v85.384
        for _ln in _lines:
            _parts.append("1 0 0 1 %g %g Tm" % (float(STAMP_STYLE.get('bleed_pt') or 0.5), _y))  # NO-CLIP v85.382  # INK-FIT v85.384
            _parts.append("(%s) Tj" % _esc(_ln))
            _y -= _lead
        _parts += ["ET", "Q"]
        _st = DecodedStreamObject()
        _st.set_data((chr(10).join(_parts)).encode("latin-1", "ignore"))
        _fnt = DictionaryObject()
        _fnt[NameObject("/Type")] = NameObject("/Font")
        _fnt[NameObject("/Subtype")] = NameObject("/Type1")
        _fnt[NameObject("/BaseFont")] = NameObject("/Helvetica-Bold")
        _fnt[NameObject("/Encoding")] = NameObject("/WinAnsiEncoding")
        _fonts = DictionaryObject()
        _fonts[NameObject("/TT1")] = wr._add_object(_fnt)
        _res = DictionaryObject()
        _res[NameObject("/Font")] = _fonts
        _st[NameObject("/Type")] = NameObject("/XObject")
        _st[NameObject("/Subtype")] = NameObject("/Form")
        _st[NameObject("/FormType")] = NumberObject(1)
        _st[NameObject("/BBox")] = ArrayObject([FloatObject(0), FloatObject(0), FloatObject(float(w)), FloatObject(float(h))])
        _st[NameObject("/Resources")] = _res
        annot[NameObject("/AP")] = DictionaryObject({NameObject("/N"): wr._add_object(_st)})
    except Exception:
        pass


def _strip_stamps(wr):  # STAMP-ONE-ALL v85.346: an older Sunsoft stamp goes even when it sits on another page
    try:
        for _pg in wr.pages:
            _keep = ArrayObject()
            for _ref in (_pg.get("/Annots") or []):
                _o = _ref.get_object()
                if str(_o.get("/Subtype")) == "/FreeText" and "Sunsoft" in str(_o.get("/Contents") or ""):
                    continue                      # an older stamp of ours goes, on any page
                _keep.append(_ref)
            _pg[NameObject("/Annots")] = _keep
    except Exception:
        pass


def _write_tag(new_pdf, text, src_w, src_h, size=None, font=None, colour=None, page=None):  # NO-LITERALS v85.264: the look comes from the source block  # OPEN-STAMP v85.350
    size = STAMP_STYLE['font_size']  # SIGNATURE-SIZE v85.275: the master's size, always - copying a twin's unspecified/small font is how Saheel's stamp came out tiny
    font = STAMP_STYLE['font']
    colour = STAMP_STYLE['colour']
    w, h = need_size(text, src_w, src_h)
    pno, box, ov = best_spot(new_pdf, w, h, page) if page else (best_spot_ink(new_pdf, w, h) if best_spot_ink(new_pdf, w, h)[0] is not None else best_spot(new_pdf, w, h))  # INK-SPOT v85.262  # OPEN-STAMP v85.350
    if box is None:
        return False, 'no place found in new CV'
    wr = PdfWriter(clone_from=new_pdf)
    _ensure_stamp_font(wr)  # FONT-RES v85.288: declare the bold face before using it
    try:
        _keep = ArrayObject()                         # STAMP-ONE v85.345: one stamp per paper - never a stack
        for _ref in (wr.pages[pno].get("/Annots") or []):
            _o = _ref.get_object()
            if str(_o.get("/Subtype")) == "/FreeText" and "Sunsoft" in str(_o.get("/Contents") or ""):
                continue                              # an older stamp of ours goes
            _keep.append(_ref)
        _strip_stamps(wr)  # STAMP-ONE-ALL v85.346
    except Exception:
        pass
    wr.add_annotation(page_number=pno,
                      annotation=FreeText(text=text, rect=box, font='Helvetica-Bold', bold=True,
                                          font_size='0pt', font_color=colour, border_color=None,
                                          background_color=None))
    try:
        for ref in wr.pages[pno]['/Annots']:
            o = ref.get_object()
            if str(o.get('/Subtype')) == '/FreeText':
                _rgb = tuple(int(colour[k2:k2 + 2], 16) / 255.0 for k2 in (0, 2, 4))  # NO-LITERALS v85.264
                o[NameObject('/DA')] = TextStringObject('/%s %g Tf %.3f %.3f %.3f rg' % ((font, da_size(size)) + _rgb))  # BOLD-LOCK v85.287: an explicit bold size keeps the bold face - 0 Tf dropped it  # SIZE-REAL v85.345  # DA-COUNTER v85.368
                o[NameObject('/DS')] = TextStringObject('font: bold %gpt %s;color:#%s' % (size, font, colour))
                o[NameObject('/Q')] = NumberObject(0)
                _draw_ap(wr, o, text, box[2] - box[0], box[3] - box[1], size, colour)  # AP-OWN v85.357  # LEFT-QUAD v85.282: left-justified - a centred block reads as a box twice its width  # AP-OWN v85.357
    except Exception:
        pass
    tmp = new_pdf + '.tmp'
    try:
        wr.write(tmp)
        shutil.move(tmp, new_pdf)
    except Exception:
        try:
            if os.path.exists(tmp): os.remove(tmp)   # TMP-SELF-CLEAN v85.338: our own scratch never becomes litter
        except Exception:
            pass
        raise
    return True, 'tagged p%d (overlap %.0f)' % (pno + 1, ov or 0)


def apply_stamp(old_pdf, new_pdf, page=None):  # OPEN-STAMP v85.350  # STAMP-ONE-WRITER v85.367: the copy path hands the text and the box to _write_tag - one writer, one DA string, one geometry
    """copy the tag from old to new. the old file is never written."""
    st = stamp_from(old_pdf)
    if not st:
        return False, 'old stamp incomplete or absent - not copied'
    # APPLY-24 v85.356: the copy path writes the masters size, never a 12pt duplicate
    # AP-REQUIRE v85.358: the copy path declares the bold face and its own appearance too
    # TMP-SELF-CLEAN v85.338: our own scratch never becomes litter
    # INK-SPOT v85.262: the copy path keeps preferring the ink spot - _write_tag already carries that line
    return _write_tag(new_pdf, st['text'], st['w'], st['h'], page=page)


def decide(old_folder, tag_ok, new_folder=None):
    """what happens AFTER the tag: ('move'|'stay'|'hold', reason).
    RULE-UPDATE v2 (master, 18 Nov): a CV dropped straight into Ready for Manager Review keeps its place and is
    only tagged; the old CV may sit anywhere in the position folder; an incomplete tag always holds.
    """
    if not tag_ok:
        return 'hold', 'the old tag is incomplete - tagged but not moved'
    if new_folder and new_folder == READY:
        return 'stay', 'already in Ready for Manager Review - tagged in place'
    if old_folder in HOLD_FOLDERS:
        return 'hold', 'the original sits in Closed - tagged but not moved'
    return 'move', 'tag first, then Ready for Manager Review'


def _cvs(root):
    """(path, folder, loose) for every pdf under root that is not a description or a shelf paper"""
    import butler
    out = []
    rootabs = os.path.abspath(root)
    for dp, dn, fn in os.walk(root):
        base = os.path.basename(dp)
        if base in ('Converted Files', 'Converted Doc Files', 'JD Files', 'Summaries'):
            continue
        for f in fn:
            if not f.lower().endswith('.pdf'):
                continue
            p = os.path.join(dp, f)
            if butler._jd_like_name(f) or butler._portal_name(f) or butler._client_doc(p):
                continue
            out.append((p, dp, os.path.abspath(dp) == rootabs))
    return out


def _strong(p):  # SHARED-WITNESS v85.248: an email or a phone is a witness; a name alone is not
    import butler
    out = set()
    try:
        for k in butler._ident_of(p):
            k = str(k)
            if '@' in k or k.isdigit():
                out.add(k)
    except Exception:
        pass
    return out


def _clusters(entries):  # SHARED-WITNESS v85.248: two papers are one person when ANY strong witness is shared
    n = len(entries)
    up = list(range(n))

    def find(i):
        while up[i] != i:
            up[i] = up[up[i]]
            i = up[i]
        return i

    seen = {}
    for i, (p, dp, loose) in enumerate(entries):
        for k in _strong(p):
            if k in seen:
                a, b = find(seen[k]), find(i)
                if a != b:
                    up[a] = b
            else:
                seen[k] = i
    groups = {}
    for i, e in enumerate(entries):
        groups.setdefault(find(i), []).append(e)
    return list(groups.values())


def _stamp_annotations(p):  # PLACE-ON-SPEC v85.268: every Sunsoft stamp on the paper, with its rect and its move-marker
    out = []
    try:
        r = PdfReader(p)
    except Exception:
        return out
    for pno, pg in enumerate(r.pages):
        for ref in (pg.get('/Annots') or []):
            o = ref.get_object()
            if str(o.get('/Subtype')) != '/FreeText':
                continue
            txt = str(o.get('/Contents') or '')
            if 'Sunsoft' not in txt and 'Total Experience' not in txt:
                continue
            out.append({'page': pno, 'rect': [float(v) for v in o.get('/Rect')], 'nm': str(o.get('/NM') or ''), 'text': txt})
    return out


def stamp_off_spec(p, rec):  # PLACE-ON-SPEC v85.268: inside the page with a 30 pt margin, left edge near the text column
    try:
        x0, y0, x1, y1 = rec['rect']
        with pdfplumber.open(p) as d:
            if rec['page'] >= len(d.pages):
                return True
            page = d.pages[rec['page']]
            W, H = float(page.width), float(page.height)
            if x0 < 10 or y0 < STAMP_PLACEMENT['page_margin'] or x1 > W - 10 or y1 > H - 10:
                return True
            ws = page.extract_words()
            left = min((float(w['x0']) for w in ws), default=x0)
            if abs(x0 - left) > 24:
                return True
        return False
    except Exception:
        return False


def stamp_mark_moved(p, rec):  # PLACE-ON-SPEC v85.268: the marker that says 'this stamp has been placed once - leave it'
    try:
        wr = PdfWriter(clone_from=p)
        for ref in (wr.pages[rec['page']].get('/Annots') or []):
            o = ref.get_object()
            if str(o.get('/Subtype')) != '/FreeText':
                continue
            if [float(v) for v in o.get('/Rect')] == rec['rect']:
                o[NameObject('/NM')] = TextStringObject('sunsoft-moved-once')
        tmp = p + '.marking'
        wr.write(tmp)
        shutil.move(tmp, p)
        return True
    except Exception:
        return False


def move_stamp(p, dry=False):  # MOVE-STAMP v85.267: the butler's ONLY placement act - it moves the rectangle, never the words
    """Move an existing Sunsoft stamp to the ink-chosen spot. Text, size, colour and every other byte are untouched."""
    import tempfile as _tf
    try:
        r = PdfReader(p)
    except Exception as ex:
        return (False, 'unreadable: %s' % ex)
    for pno, pg in enumerate(r.pages):
        for ref in (pg.get('/Annots') or []):
            o = ref.get_object()
            if str(o.get('/Subtype')) != '/FreeText':
                continue
            rect = [float(v) for v in o.get('/Rect')]
            w = rect[2] - rect[0]
            h = rect[3] - rect[1]
            if w <= 0 or h <= 0:
                return (False, 'a stamp with no size cannot be moved')
            bare = _os_path = None
            try:
                bare = _tf.mkstemp(suffix='.pdf')[1]
                _wr = PdfWriter(clone_from=p)
                for _pg in _wr.pages:
                    if '/Annots' in _pg:
                        _keep = [a for a in _pg['/Annots'] if str(a.get_object().get('/Subtype')) != '/FreeText']
                        if _keep:
                            _pg[NameObject('/Annots')] = ArrayObject(_keep)
                        else:
                            del _pg[NameObject('/Annots')]
                _wr.write(bare)
            except Exception as ex:
                return (False, 'could not measure cleanly: %s' % ex)
            pno2, box, ov = best_spot_ink(bare, w, h)
            if box is None:
                pno2, box, ov = best_spot(bare, w, h)
            if box is None:
                return (False, 'no clean band - held for the master')
            if dry:
                return (True, 'would move page %d %s -> %s' % (pno + 1, [round(v) for v in rect], [round(v) for v in box]))
            wr = PdfWriter(clone_from=p)
            moved = 0
            for _pg in wr.pages[pno].get('/Annots') or []:
                o2 = _pg.get_object()
                if str(o2.get('/Subtype')) != '/FreeText':
                    continue
                o2[NameObject('/Rect')] = RectangleObject([float(box[0]), float(box[1]), float(box[2]), float(box[3])])
                moved += 1
            tmp = p + '.moving'
            wr.write(tmp)
            shutil.move(tmp, p)
            return (True, 'moved %d stamp(s) to page %d %s (rect only)' % (moved, pno2 + 1, [round(v) for v in box]))
    return (False, 'no stamp to move')


def same_person(a, b):  # IDENTITY-WITNESS v85.301: two papers are ONE human only by a shared phone or email - a name may confirm, never prove
    try:
        import re as _re
        _pa = set(str(x)[-10:] for x in ((a or {}).get("phones") or []) if str(x)[-10:].isdigit())
        _pb = set(str(x)[-10:] for x in ((b or {}).get("phones") or []) if str(x)[-10:].isdigit())
        _ea = set(str(x).strip().lower() for x in ((a or {}).get("emails") or []) if x)
        _eb = set(str(x).strip().lower() for x in ((b or {}).get("emails") or []) if x)
        if not ((_pa & _pb) or (_ea & _eb)):
            return False
        _na = _re.sub(r"[^a-z0-9]+", " ", str((a or {}).get("name") or "").lower()).strip()
        _nb = _re.sub(r"[^a-z0-9]+", " ", str((b or {}).get("name") or "").lower()).strip()
        if not _na or not _nb:
            return True
        return _na == _nb or _na in _nb or _nb in _na
    except Exception:
        return False

def stamp_on_arrival(p, say=print):  # STAMP-READY-TWIN v85.274: the Ready folder is the stamp room - same-folder twin first, name-confirmed
 """A CV in Ready for Manager Review receives its twin's stamp: same Ready folder first (file name, then phone/email, confirmed by name), the position only as fallback. Content is copied faithfully; an existing stamp is never touched."""
 import os as _os, json as _j, time as _t, re as _re
 import butler as _b
 def _norm(x):
  return _re.sub(r'[^a-z0-9]+', ' ', str(x or '').lower()).strip()
 try:
  par = _os.path.dirname(p)
  if _os.path.basename(par) != 'Ready for Manager Review':
   return ('skip', 'not a Ready arrival')
  if has_stamp(p):
   return ('skip', 'already stamped - left alone (the tidy is suspended until compare-first)')
  pos = _os.path.dirname(par)
  try:
   ids = _b.identity_of(p) or {}
  except Exception:
   ids = {}
  ph = set(str(x)[-10:] for x in (ids.get('phones') or []) if str(x)[-10:].isdigit())
  em = set(str(x).strip().lower() for x in (ids.get('emails') or []) if x)
  nm = _norm(ids.get('name'))
  if not (ph or em or nm):
   return ('report', 'no witness readable - left alone')
  stem = _norm(_os.path.splitext(_os.path.basename(p))[0])
  def _twin_ok(q):
   if _os.path.abspath(q) == _os.path.abspath(p):
    return False
   try:
    blk = stamp_from(q)
   except Exception:
    return False
   if not blk or not (blk.get('text') or '').strip():
    return False
   try:
    j = _b.identity_of(q) or {}
   except Exception:
    j = {}
   jp = set(str(x)[-10:] for x in (j.get('phones') or []) if str(x)[-10:].isdigit())
   je = set(str(x).strip().lower() for x in (j.get('emails') or []) if x)
   jn = _norm(j.get('name'))
   same_stem = _norm(_os.path.splitext(_os.path.basename(q))[0]) == stem
   witness = bool(ph & jp) or bool(em & je)
   name_ok = bool(nm) and bool(jn) and (nm == jn or nm in jn or jn in nm)
   return same_person(ids, j)  # IDENTITY-WITNESS v85.301
  src = None; scope = ''
  try:
   for f in sorted(_os.listdir(par)):
    q = _os.path.join(par, f)
    if f.lower().endswith('.pdf') and _os.path.isfile(q) and _twin_ok(q):
     src = q; scope = 'ready-folder'; break
  except Exception:
   pass
  if src is None:
   for dp, dn, fn in _os.walk(pos):
    for f in fn:
     q = _os.path.join(dp, f)
     if f.lower().endswith('.pdf') and _twin_ok(q):
      src = q; scope = 'position'; break
    if src:
     break
  if src is None:
   return ('report', 'no complete twin in this position - reported, never invented')
  blk = stamp_from(src) or {}
  ok, msg = _write_tag(p, blk.get('text') or '', blk.get('w'), blk.get('h'), blk.get('size'), blk.get('font'), blk.get('colour'))
  try:
   row = {'ts': int(_t.time()), 'file': _os.path.basename(p), 'source': _os.path.basename(src), 'scope': scope, 'result': msg}
   open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'notes', 'stamp_journal.jsonl'), 'a').write(_j.dumps(row) + chr(10))
  except Exception:
   pass
  return ('stamped' if ok else 'report', '%s <- %s [%s] | %s' % (_os.path.basename(p), _os.path.basename(src), scope, msg))
 except Exception as ex:
  return ('report', 'error: %s' % ex)
def refresh_flow(root, say=print, do_move=False):
    """TAG-ONLY v85.240  # NO-COUPLE v85.240: the butler never moves a file.
    Files move only by their own file tags (the existing tag machinery). This flow does ONE thing: the latest CV
    of a known candidate receives the Sunsoft Technology tag from its twin, anywhere in the position folder.
    """
    import butler
    done = hold = 0
    for g in _clusters(_cvs(root)):  # SHARED-WITNESS v85.248: cluster by shared phone/email
        if len(g) < 2:
            continue
        items = g
        new_p, new_dp, _loose = max(items, key=lambda t: os.path.getmtime(t[0]))
        others = [t for t in items if t[0] != new_p]
        stamped = [t for t in others if stamp_from(t[0])]
        if not stamped or has_stamp(new_p):
            continue
        old_p, old_dp, _ = max(stamped, key=lambda t: os.path.getmtime(t[0]))
        ok, msg = apply_stamp(old_p, new_p)
        if not ok:
            _txt = any_stamp_text(old_p)
            if _txt:
                ok2, msg2 = _write_tag(new_p, _txt, 258, 116)
                if ok2:
                    say('🏷️ %s ← %s | %s (incomplete tag carried - fix it by hand)' % (
                        os.path.basename(new_p), os.path.basename(old_p), msg2))
                    hold += 1
                    continue
            say('⏸️ %s: no usable Sunsoft tag on the twin - nothing copied' % os.path.basename(new_p))
            hold += 1
            continue
        say('🏷️ %s ← %s | %s' % (os.path.basename(new_p), os.path.basename(old_p), msg))
        done += 1
    return done, hold
