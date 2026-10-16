import os, re, json, time, hashlib
BASE = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.join(BASE, 'fit_weights.json'); STORE = os.path.join(BASE, 'fit_rank')
DEFAULT_W = {'keywords': 40, 'years': 20, 'designation': 20, 'location': 10, 'notice': 5, 'ctc': 5}
STOP = set(("the and for with from have has had will would can could should must role job work experience years year months strong good excellent etc a an in on at of to by is are as we you our their his her or not required preferred candidate candidates looking seeking ability proven track responsible responsibilities knowledge understanding handling manage managed managing skills skill").split())
def _cfg():
    if not os.path.exists(CFG): json.dump({'weights': DEFAULT_W, 'ack_min': 10, 'eod_cutoff': '16:30'}, open(CFG, 'w'), indent=2)
    return json.load(open(CFG))
def _pdf_text(p):
    t = ''
    try:
        import pdfplumber; out = []
        with pdfplumber.open(p) as pdf:
            for pg in pdf.pages[:4]: out.append(pg.extract_text() or '')
        t = '\n'.join(out)
    except Exception: t = ''
    if len(t.strip()) < 40:
        try:
            import butler
            t = butler.extract_text_ocr(p) or t
        except Exception: pass
    return t
def _docx_text(p):
    try:
        import zipfile
        x = zipfile.ZipFile(p).read('word/document.xml').decode('utf8', 'ignore')
        return re.sub(r'<[^>]+>', ' ', x)
    except Exception: return ''
def _eml_text(p):
    try:
        import email, email.policy
        m = email.message_from_file(open(p, errors='ignore'), policy=email.policy.default)
        b = m.get_body(preferencelist=('plain', 'html'))
        return b.get_content() if b else ''
    except Exception: return ''
def _text(p):
    l = p.lower()
    if l.endswith('.pdf'): return _pdf_text(p)
    if l.endswith('.docx'): return _docx_text(p)
    if l.endswith(('.eml', '.msg')): return _eml_text(p)
    if l.endswith('.doc'):
        c = os.path.join(os.path.dirname(p), 'Converted Files', os.path.splitext(os.path.basename(p))[0] + '.pdf')
        return _pdf_text(c) if os.path.exists(c) else ''
    return ''
def _kw(t, n=30):
    f = {}
    for x in re.findall(r"[a-z][a-z\-]{2,}", t.lower()):
        if x not in STOP: f[x] = f.get(x, 0) + 1
    return [x for x, _ in sorted(f.items(), key=lambda kv: -kv[1])[:n]]
def _years(t):
    m = [int(x) for x in re.findall(r'(\d{1,2})\s*(?:years|yrs)', t.lower())]
    return max(m) if m else None
def _notice(t):
    m = re.search(r'(\d{1,3})\s*days?\s*(?:notice|np)', t.lower()) or re.search(r'notice\s*(?:period)?\s*[:\-]?\s*(\d{1,3})\s*days', t.lower())
    return int(m.group(1)) if m else None
def _ctc(t):
    m = re.search(r'(\d{1,2}(?:\.\d+)?)\s*(?:lpa|lakhs?|lacs?)', t.lower())
    return float(m.group(1)) if m else None
def _loc(t):
    c = ['mumbai','bengaluru','bangalore','delhi','gurugram','gurgaon','noida','pune','chennai','hyderabad','ahmedabad','kolkata','jaipur','lucknow','indore','nagpur','thane','vikhroli','erode','coimbatore']
    return [x for x in c if x in t.lower()]
def _desig(t):
    return re.findall(r'\b(regional|area|zone|sales|service|product|technical|support|manager|head|lead|engineer|executive|officer|director|vp|gm|agm|dgm)\b', t.lower())
def rank(cv, jd, w):
    reasons, reds = [], []
    jk, ck = set(_kw(jd, 40)), set(_kw(cv, 60))
    ov = len(jk & ck) / max(1, len(jk)); s = w['keywords'] * ov
    if ov > 0.35: reasons.append(f'strong keyword match ({int(ov*100)}%)')
    jy, cy = _years(jd), _years(cv)
    if jy and cy:
        g = cy - jy
        if g >= 0: s += w['years']; reasons.append(f'{cy}y exp meets JD {jy}y')
        elif g >= -2: s += w['years'] * 0.6; reasons.append(f'{cy}y close to JD {jy}y')
        else: reds.append(f'exp {cy}y well below JD {jy}y')
    jd_, cd_ = set(_desig(jd)), set(_desig(cv))
    do = len(jd_ & cd_) / max(1, len(jd_)); s += w['designation'] * do
    if do > 0.5: reasons.append('designation family aligns')
    jl, cl = set(_loc(jd)), set(_loc(cv))
    if jl and cl:
        if jl & cl: s += w['location']; reasons.append('location aligns')
        else: reds.append('location mismatch')
    n = _notice(cv)
    if n is not None:
        if n <= 60: s += w['notice']; reasons.append(f'notice {n}d')
        elif n > 90: reds.append(f'notice {n}d')
    jc, cc = _ctc(jd), _ctc(cv)
    if jc and cc:
        if cc <= jc * 1.3: s += w['ctc']; reasons.append('CTC in band')
        else: reds.append(f'CTC {cc}L above band {jc}L')
    score = int(min(100, s)); tier = 'A' if score >= 65 else ('B' if score >= 40 else 'C')
    return {'score': score, 'tier': tier, 'reasons': reasons[:3], 'red_flags': reds[:3]}
def positions(root):
    out = []
    for c in sorted(os.listdir(root)):
        cp = os.path.join(root, c)
        if not os.path.isdir(cp) or c.startswith('.'): continue
        for p in sorted(os.listdir(cp)):
            pp = os.path.join(cp, p)
            if os.path.isdir(pp) and not p.startswith('.'): out.append(pp)
    return out
def _jd_for(pos):
    sp0 = _store(pos)
    if os.path.exists(sp0):
        d0 = json.load(open(sp0))
        if d0.get('jdtext'): return d0['jdtext'], d0.get('jd')
    for f in os.listdir(pos):
        l = f.lower()
        if l.startswith('jd') or ' jd' in l or '_jd' in l or l.endswith(('.eml', '.msg')):
            t = _text(os.path.join(pos, f))
            if t.strip(): return t, f
    return None, None
def _store(pos):
    os.makedirs(STORE, exist_ok=True)
    return os.path.join(STORE, hashlib.md5(pos.encode()).hexdigest()[:8] + '.json')
def tick(B, say=lambda m: None):
    w = _cfg()['weights']
    for pos in positions(B.root):
        jdt, jdf = _jd_for(pos)
        if not jdt: continue
        sp = _store(pos)
        d = json.load(open(sp)) if os.path.exists(sp) else {'jd': jdf, 'ctx': jdt[:300], 'rows': {}}
        d['jdtext'] = jdt
        ch = False
        for f in os.listdir(pos):
            fp = os.path.join(pos, f)
            lf = f.lower()
            if not lf.endswith('.pdf') or not os.path.isfile(fp): continue
            if lf.startswith('jd') or ' jd' in lf or '_jd' in lf: continue
            st = os.stat(fp); key = f'{st.st_mtime_ns}|{st.st_size}'
            if d['rows'].get(f, {}).get('key') == key: continue
            txt = _text(fp)
            if not txt.strip(): continue
            r = rank(txt, jdt, w); r['key'] = key; r['at'] = int(time.time()); r['called'] = d['rows'].get(f, {}).get('called', False)
            d['rows'][f] = r; ch = True
        budget = 3
        for sub in sorted(os.listdir(pos)):
            sp2 = os.path.join(pos, sub)
            if not os.path.isdir(sp2) or sub.startswith('.'): continue
            for f in os.listdir(sp2):
                if budget <= 0: break
                fp = os.path.join(sp2, f); lf = f.lower()
                if not lf.endswith('.pdf') or lf.startswith('jd') or ' jd' in lf: continue
                st = os.stat(fp); key = f'{st.st_mtime_ns}|{st.st_size}'
                if d['rows'].get(f, {}).get('key') == key: continue
                txt = _text(fp)
                if not txt.strip(): continue
                r = rank(txt, jdt, w); r['key'] = key; r['at'] = int(time.time()); r['called'] = d['rows'].get(f, {}).get('called', False); r['sub'] = sub
                d['rows'][f] = r; ch = True; budget -= 1
        if ch: json.dump(d, open(sp, 'w'), indent=2)
def _phone_for(path):
    try:
        d = json.load(open(os.path.join(BASE, 'phones.json')))
        e = d.get(path) or next((v for k, v in d.items() if os.path.basename(k).lower() == os.path.basename(path).lower()), None)
        if e and e.get('phones'): return '+' + str(e['phones'][0])
    except Exception: pass
    return None
def show(root, arg, mode='call', say=print):
    pos = None; cands = positions(root)
    if arg:
        hit = [p for p in cands if arg.lower() in os.path.basename(p).lower()]
        pos = hit[0] if hit else None
    if not pos:
        try:
            import briefing; f = briefing._read_focus()
            if f and f.get('path') and os.path.isdir(f['path']): pos = f['path']
        except Exception: pass
    if not pos: say('usage: call [position words]  (or focus a position first)'); return
    sp = _store(pos)
    say(f'no rankings yet for {os.path.basename(pos)} - JD ' + ('found; ranking fills within a few sweeps' if _jd_for(pos)[0] else 'MISSING in this folder'))
    d = json.load(open(sp))
    rows = sorted(d['rows'].items(), key=lambda kv: ({'A': 0, 'B': 1, 'C': 2}[kv[1]['tier']], -kv[1]['score']))
    if mode == 'call':
        say(f"📋 {os.path.basename(pos)}  (JD: {d.get('jd')})")
        for f2, r in rows:
            say(f" {'✅' if r.get('called') else '  '} [{r['tier']}] {r['score']:3d} · {os.path.splitext(f2)[0]}")
            for x in r['reasons'][:2]: say(f'        + {x}')
            for x in r['red_flags']: say(f'        - {x}')
    else:
        nxt = next(((f2, r) for f2, r in rows if r['tier'] == 'A' and not r.get('called')), None) or next(((f2, r) for f2, r in rows if not r.get('called')), None)
        if not nxt: say('everyone ranked has been called'); return
        f2, r = nxt
        say(f"➡️ next: {os.path.splitext(f2)[0]}  [{r['tier']} {r['score']}]  phone: {_phone_for(os.path.join(pos, f2)) or '??'}")
        for x in r['reasons'][:2]: say(f'     + {x}')
        for x in r['red_flags']: say(f'     - {x}')
        say(f'     then: wa "{os.path.splitext(f2)[0]}"')
def mark_called(path):
    sp = _store(os.path.dirname(path))
    if not os.path.exists(sp): return
    d = json.load(open(sp)); f = os.path.basename(path)
    if f in d['rows']:
        d['rows'][f]['called'] = True
        json.dump(d, open(sp, 'w'), indent=2)
