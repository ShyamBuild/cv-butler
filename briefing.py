VERSION = '85.0'  # THE FREEZE v85.0: the standing price of every future change
import butler  # LISTEN v81.67: the REPL teaches through the butler's book (module scope: the loop lives here)
import os, re, sys, datetime, json, urllib.request
import logging, warnings
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
warnings.filterwarnings("ignore")
logging.lastResort = logging.NullHandler()
for _n in ("pdfminer", "fontTools"):
    _l = logging.getLogger(_n); _l.addHandler(logging.NullHandler()); _l.setLevel(logging.CRITICAL)

TAGS = [
    ("interview today",    "🔴 INTERVIEWS TODAY", "confirm on-the-way / venue (or virtual link)"),
    ("interview tomorrow", "🟠 INTERVIEWS TOMORROW", "1-day-before confirmation call"),
    ("interview scheduled","📅 INTERVIEWS SCHEDULED", ""),
    ("call scheduled",     "📞 MISSED-CALL FOLLOW-UPS", "didn't answer 1st call - call again"),
    ("feedback pending",   "🕓 FEEDBACK PENDING", "nudge client/manager"),
    ("ready for manager review", "🧾 MANAGER REVIEW", ""),
    ("awaiting cv update", "✍️ CV UPDATE DUE", ""),
    ("awaiting jd confirmation", "📤 JD SHARED - ACK PENDING", "acknowledgement awaited"),
    ("interview cleared",        "🎉 INTERVIEW CLEARED", "next round / offer"),
    ("expected to join",         "🚪 EXPECTED TO JOIN", "onboarding follow-up"),
    ("joined - payment pending", "💰 JOINED - PAYMENT PENDING", "invoice follow-up"),
    ("payment received",         "✅ PAYMENT RECEIVED", ""),
    ("closed - not proceeding",  "🚫 CLOSED - NOT PROCEEDING", "tag removed = off the board"),
    ("rejected by client",       "❌ REJECTED BY CLIENT", ""),
    ("position active",          "🟢 POSITION ACTIVE", ""),
    ("position on hold",         "🟡 POSITION ON HOLD", ""),
    ("position closed",          "⚫ POSITION CLOSED", ""),
]

FOCUS_SKIP = {t for t, _, _ in TAGS} | {'rejected by client', 'closed – not proceeding', 'closed - not proceeding',
    'interview cleared', 'expected to join', 'joined - payment pending', 'payment received', 'position active',
    'position on hold', 'position closed', 'awaiting jd confirmation', 'awaiting cv update', 'ready for manager review',
    'converted doc files', 'converted files', 'duplicates', 'nvites', 'ta_output'}

def clean_pos(name):
    name = (name or '').replace('|', ' ')  # PIPE-CLEAN v67
    n = re.sub(r'^jd[\s_-]+', '', name, flags=re.I)
    n = n.replace('_', ' ').replace('-', ' ')
    n = re.sub(r'\b(pvt\.?|ltd\.?|llp|inc\.?|corp\.?|projects|technologies|solutions|enterprises|international|india)\b', ' ', n, flags=re.I)
    n = re.sub(r'\s*\.\s*', ' ', n)
    return re.sub(r'\s+', ' ', n).strip()

def short_pos(p, w=31):
    return p if len(p) <= w else p[:w-1] + '…'

_PHONE_CACHE = {}
PHONES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phones.json")
PHONE_RE = re.compile(r'(?:\+?91[\s\-\.]?)?([6-9](?:[\s\-\.]?\d){9})')
def phones_in_text(t):
    out = []
    for m in PHONE_RE.finditer(t or ''):
        d = re.sub(r'\D', '', m.group(1))
        if d not in out: out.append(d)
    return out
def phones_of(path):  # ONE-CLERK v81.72: every voice asks the butler's clerk - taught book, email witness, OCR, confession, all of it
    _lb = _phones_by_basename(path)
    if _lb: return _lb
    try:
        _bp = butler.phones_of(path)
        if _bp: return _bp
    except Exception: pass
    return _phones_of_local(path)

def _phones_of_local(path):  # ONE-CLERK v81.72: the old clerk, kept as last resort only
    _ov = _fix_load().get(re.sub(r'[^a-z]', '', os.path.splitext(os.path.basename(path))[0].lower()))
    if _ov: return _ov if isinstance(_ov, list) else [_ov]
    try: store = json.load(open(PHONES_FILE))
    except Exception: store = {}
    try:
        st = os.stat(path); k = f"{st.st_ino}|{st.st_mtime}|{st.st_size}"
    except OSError:
        return []
    e = store.get(os.path.abspath(path))
    if e and e.get('k') == k and e.get('phones') is not None: return e['phones']
    txt = ''
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            txt = "\n".join((pg.extract_text() or '') for pg in pdf.pages[:2])
    except Exception: pass
    if not txt.strip():
        try:
            import butler as _b; txt = _b.extract_text_ocr(path)
        except Exception: txt = ''
    ph = phones_in_text(txt)
    if not ph:
        try:
            import butler as _b2; ocr = _b2.extract_text_ocr(path)
        except Exception:
            ocr = ''
        if ocr.strip(): ph = phones_in_text(ocr)
    _lb = _phones_by_basename(path)
    if _lb: ph = _lb
    store[os.path.abspath(path)] = {'k': k, 'phones': ph}
    try: json.dump(store, open(PHONES_FILE, 'w'))
    except Exception: pass
    return ph
def _pick_phone(ps, say=print, ask=None, path=None):
    if path is not None and len(ps) > 1:  # PROVENANCE-AT-PICK v81.92 # CANDIDATE-FIRST v81.93: when the paper distinguishes the human from a referee, the machine picks the human and says so; the list returns only for true ambiguity (markers separated by space-hash, never by plus: each witness keeps its own hash)
        try:
            _lv = butler.provenance_of(path, ps) or []
            _cand = [x for x, w in _lv if 'referee' not in w]
            if len(_cand) == 1 and _cand[0] in ps:
                say(f"🎯 using the candidate's own number {_cand[0]} (page-proven); a referee-suspect number stays un-dialled unless you name it")
                return _cand[0]
        except Exception:
            pass
    if not ps: return ''
    if len(ps) == 1: return ps[0]
    for i, x in enumerate(ps): say(f"   {i+1}) {x}")
    a = ask or (lambda pr: input(pr))
    try: return ps[int(a("   pick phone #: ").strip()) - 1]
    except Exception: return ps[0]
def phone_of(path):
    ps = phones_of(path)
    return ps[0] if ps else ''
COLOR_TAGS = {'Red','Orange','Yellow','Green','Blue','Purple','Gray','Grey'}
SKIP_DIRS = {'converted doc files', 'converted files', 'duplicates', 'previous versions'}
TAGS_CACHE = os.path.join(BASE_DIR, 'tags_cache.json')
def _load_tags_cache():
    try: return json.load(open(TAGS_CACHE))
    except Exception: return {}
def _save_tags_cache(c):
    try: json.dump(c, open(TAGS_CACHE, 'w'))
    except Exception: pass
def _xattr_crc(path):
    try:
        import zlib
        return zlib.crc32(os.getxattr(path, 'com.apple.metadata:_kMDItemUserTags'))
    except Exception:
        return 0
def _tags_of(path):
    try:
        import plistlib
        arr = plistlib.loads(os.getxattr(path, 'com.apple.metadata:_kMDItemUserTags'))
        out = []
        for t in arr:
            nm = str(t).split('\n')[0].strip()
            if nm and nm not in COLOR_TAGS: out.append(nm)
        return out
    except Exception:
        try:
            r = subprocess.run(['mdls', '-name', 'kMDItemUserTags', path], capture_output=True, text=True, timeout=15)
            txt = (r.stdout or '').strip()
            if not txt or '(null)' in txt: return []
            tags = []
            for line in txt.splitlines():
                line = line.strip().rstrip(',')
                if line in ('(', ')') or line.startswith('kMDItemUserTags'): continue
                if line.startswith('"') and line.endswith('"'): line = line[1:-1]
                nm = line.split('\n')[0].strip()
                if nm and nm not in COLOR_TAGS: tags.append(nm)
            return tags
        except Exception:
            return []
CLIENTS_FILE = os.path.join(BASE_DIR, 'clients.json')
def _clients():
    try: return json.load(open(CLIENTS_FILE))
    except Exception: return {}
def _jd_text_for(pos_path):
    try:
        import fitrank
        sp = fitrank._store(pos_path)
        if os.path.exists(sp):
            t = json.load(open(sp)).get('jdtext')
            if t: return t
    except Exception: pass
    return ''
def _auto_client_full(short, pos_path):
    # filename-first seed v49
    try:
        for fn in os.listdir(pos_path):
            lf = fn.lower()
            if lf.startswith('jd') or '_jd' in lf or ' jd' in lf or lf.endswith(('.eml', '.msg')):
                m = re.match(r'^(?:jd|fw|fwd)[\s_\-:]*(.{2,40}?)(?:\s*[-–_|]|\.pdf|\.eml|\.msg)', fn, re.I)
                if m:
                    w = m.group(1).strip().split()
                    if w and len(w[0]) > 3: w[0] = w[0].title()
                    return ' '.join(w[:4])
    except Exception:
        pass
    head = (_jd_text_for(pos_path) or '')[:600]
    low = short.lower()
    for m in re.finditer(r'[A-Z][A-Za-z0-9&.\-]{2,24}(?:\s+[A-Z][A-Za-z0-9&.\-]{2,24}){0,3}', head):
        run = m.group(0)
        if low in run.lower():
            w = run.split()
            if len(w[0]) > 3: w[0] = w[0].title()
            return ' '.join(w)
    return ''
def _client_full(short_dirname, pos_path):
    short = re.sub(r'^\d+[\s_-]*', '', short_dirname).strip()
    m = _clients(); key = re.sub(r'[^a-z]', '', short.lower())
    if key in m: return m[key]
    full = _auto_client_full(short, pos_path)
    if full:
        m[key] = full
        try: json.dump(m, open(CLIENTS_FILE, 'w'), indent=2)
        except Exception: pass
        return full
    return short.title()
CITY_WORDS = ['bhopal', 'indore', 'surat', 'chandigarh', 'greater noida', 'vikhroli east', 'vikhroli', 'mumbai', 'bengaluru', 'bangalore', 'delhi', 'gurugram', 'gurgaon', 'noida', 'pune', 'chennai', 'hyderabad', 'ahmedabad', 'kolkata', 'jaipur', 'lucknow', 'nagpur', 'thane', 'erode', 'coimbatore']  # CITY-DEDUPE v84.29: a law-list holds no twins
def _split_pos(pos):
    low = (pos or '').lower().replace('|', ' ')  # SPLIT-HARD v56
    low = re.sub(r'\blocation\b', ' ', low)
    locs = []
    for c in CITY_WORDS:
        if c in low:
            locs.append(c.title()); low = low.replace(c, ' ')
    title = re.sub(r'\s+', ' ', low).strip(' -|,')
    seen = []
    for x in locs:
        if x not in seen: seen.append(x)
    return ((title.title() if title else pos), ', '.join(seen))
class _SafeDict(dict):
    def __missing__(self, k): return ''
def _fmt_tpl(tpl, hit, f, name):
    try:  # POS-ID v84.21: every draft, keyword or chair, shows the position's triple before the window opens
        if hit and os.path.isfile(str(hit)):
            import butler as _bt; _bt.say_identity_for(str(hit), print)
    except Exception: pass
    pos, cli = _pos_client_for(hit, f)
    title, loc = _split_pos(pos)
    try:  # REGISTRY-VOICE v84.28: the taught truths outrank the path guesses inside the message itself
        import butler as _bt
        _idn = _bt.pos_identity(str(hit)) if (hit and os.path.isfile(str(hit))) else {}
        if _idn.get('company'): cli = _idn['company']
        if _idn.get('role'): title = _idn['role']
        if _idn.get('loc'): loc = _idn['loc']
        _dz = _idn.get('designation') or title  # DESIG-FALLBACK v84.29: the designation slot is never blank - it borrows the position's name when untold
    except Exception:
        _dz = ''
    where = f"Company: {cli}" + (f" | Location: {loc}" if loc else "")
    at = cli + (f", {loc}" if loc else "")
    try:
        return tpl.format(name=name, position=title, company=cli, location=loc or '-', where_line=where, where=at, designation=_dz, client=cli)  # CLIENT-KEY v84.42: legacy templates ask for {client}; the living registry answers
    except Exception:
        return tpl.format_map(_SafeDict(name=name, position=title, company=cli, location=loc or '-', where_line=where, where=at, designation=_dz, client=cli))
def _pos_client_for(hit, f=None):
    for base in ([os.path.dirname(os.path.abspath(hit))] if hit else []) + ([f['path']] if f and f.get('path') else []):
        comp = _company_root(base)
        rel = os.path.relpath(base, comp)
        parts = [] if rel == '.' else rel.split(os.sep)
        if len(parts) >= 2:
            pos_path = os.path.join(comp, parts[0], parts[1])
            return clean_pos(parts[1]), _client_full(parts[0], pos_path)
        if len(parts) == 1:
            pos_path = os.path.join(comp, parts[0])
            return clean_pos(parts[0]), _client_full(parts[0], pos_path)
    return 'the discussed role', 'our client'
def do_draftwhy(arg, root, say=print):  # DRAFT-WHY v84.33: eyes behind every draft - which guess, which truth, which fields, which files (display-only; _fmt_tpl stays witnessed and untouched)
    hits = _hits_for((arg or '').strip(), root)
    if not hits: say(f'🤷 no CV matches {arg!r}'); return
    p = hits[0]; nm = os.path.splitext(os.path.basename(p))[0]
    pos, cli = _pos_client_for(p, None); title, loc = _split_pos(pos)
    import butler as _bt
    idn = _bt.pos_identity(p)
    fco = idn.get('company') or cli; fpo = idn.get('role') or title; flo = idn.get('loc') or loc; fdz = idn.get('designation') or fpo
    say(f'🔎 draft anatomy for {nm}:')
    say(f'   legacy path-guess : position={title!r} company={cli!r} location={loc!r}')
    say(f'   registry truth    : company={idn.get("company")!r} role={idn.get("role")!r} loc={idn.get("loc")!r} designation={idn.get("designation")!r}')
    say(f'   fields used       : name={nm!r} · position={fpo!r} · company={fco!r} · location={flo!r} · designation={fdz!r} · where={fco + (", " + flo if flo else "")!r}')
    TDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    for w in ('jd', 'missed', 'nudge', 'refer', 'awaiting'):
        try: cands = [fn for fn in sorted(os.listdir(TDIR)) if fn.endswith('.txt') and w in fn.lower()]
        except Exception: cands = []
        say(f'   scenario {w} files : ' + (', '.join(cands[:4]) or 'none'))
    say('   rendered jd draft :')
    for ln in _fmt_tpl(_tpl_for(['jd']), p, None, nm).split(chr(10)): say('     ' + ln)
    say('   queued chases     : ad_wait.build_text now drinks from the same registry (QUEUE-REGISTRY v84.34)')

def do_adlog(arg, root, say=print):  # ADLOG v81.2 (read-only)
    n = 10
    try: n = max(1, int((arg or '').strip()))
    except Exception: pass
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'butler_live.log')
    try: lines = open(p, encoding='utf-8', errors='replace').read().splitlines()
    except Exception: say('📭 no butler log yet'); return
    hits = [x for x in lines if 'autodraft' in x.lower()][-n:]
    if not hits: say('📭 no autodraft lines yet - tag a file and watch this space'); return
    for x in hits: say(x)

def do_renwhy(arg, root, say=print):
    import butler, fitrank
    hits = _hits_for((arg or '').strip(), root)
    if not hits: say(f'🤷 no CV matches {arg!r}'); return
    p = hits[0]; b = butler.Butler(root); b._jload()
    log = []
    b.handle_pdf(p, log.append)
    say(f'🔎 {os.path.relpath(p, root)}')
    say(f'   handle_pdf said: {log if log else "(silent = rename refused)"}')
    try:
        ino = os.stat(p).st_ino
        say(f'   rc={b.rc.get(ino)} rcn={getattr(b, "rcn", {}).get(ino)} journal={"yes" if b.journal.get(p) else "no"}')
    except Exception: pass
    t = fitrank._text(p)
    say(f'   text head: {" | ".join(t.split(chr(10))[:3])[:200]}')

def do_clientname(arg, root, say=print):
    if '=' not in arg: say('usage: clientname <short> = <Full Client Name>'); return
    q, full = [x.strip() for x in arg.split('=', 1)]
    m = _clients(); m[re.sub(r'[^a-z]', '', q.lower())] = full
    json.dump(m, open(CLIENTS_FILE, 'w'), indent=2)
    say(f'🏢 client alias saved: {q} -> {full}')

def _pos_for(fp, root):
    d = os.path.dirname(fp)
    tagset = {k for k, _, _ in TAGS} | FOCUS_SKIP
    while d and os.path.abspath(d) != os.path.abspath(root):
        bn = os.path.basename(d).lower().replace('\u2013', '-')
        if bn not in tagset:
            return clean_pos(os.path.basename(d))
        d = os.path.dirname(d)
    return clean_pos(os.path.basename(root))
def _norm(s):
    return (s or '').lower().replace(chr(8211), '-').replace(' ', '_')

def collect(root):
    data = {k: [] for k, _, _ in TAGS}
    key_of = {_norm(k): k for k, _, _ in TAGS}
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if not d.startswith(".")]
        for f in fn:
            if not f.lower().endswith(".pdf") or f.startswith("."): continue
            fp = os.path.join(dp, f)
            tags = []
            try: tags = _tags_of(fp)
            except Exception: tags = []
            sec = None
            for t in tags:
                if _norm(t) in key_of:
                    sec = key_of[_norm(t)]; break
            if sec is None:
                rel = os.path.relpath(dp, root)
                if rel != ".":
                    top = _norm(rel.split(os.sep)[0])
                    if top in key_of: sec = key_of[top]
            if not sec: continue
            pos = _pos_for(fp, root)
            ph = ''
            try:
                ps = phones_of(fp) if 'phones_of' in globals() else [phone_of(fp)]
                ph = (ps or [''])[0] if isinstance(ps, list) else ps
            except Exception:
                try: ph = phone_of(fp)
                except Exception: ph = ""
            data[sec].append([os.path.splitext(f)[0], pos, ph])
    return data
def render(say, title, items, note):
    if not items: return 0
    say("")
    say(f"{title} ({len(items)})" + (f" — {note}" if note else ""))
    say(f"{'NAME':<22} {'POSITION':<33} PHONE")
    for n, p, ph in items:
        say(f"{n[:21]:<22} {short_pos(p):<33} {ph}")
    return len(items)

def print_briefing(root, say=print):
    data = collect(root)
    say("")
    say(f"🌅 BRIEFING — {datetime.date.today().strftime('%a %d %b')} — {os.path.basename(root)}")
    total = 0
    for k, title, note in TAGS:
        total += render(say, title, data[k], note)
    if not total: say("   ✅ nothing due right now")
    say("")

def _parse_json(raw):
    raw = raw.strip()
    if raw.startswith('```'): raw = raw.strip('`')
    if raw.lower().startswith('json'): raw = raw[4:]
    try: return json.loads(raw)
    except Exception:
        m = re.search(r'\{.*\}', raw, re.S)
        return json.loads(m.group(0)) if m else None

def ask_ollama(q):
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as r:
            names = [m['name'] for m in json.loads(r.read().decode()).get('models', []) if 'embed' not in m['name'].lower()]
        if not names: return None
        prompt = f"Tags: {[k for k,_,_ in TAGS]}. Today is {datetime.date.today()}. For the user's question, reply with ONLY JSON like {{\"tags\":[\"interview tomorrow\"],\"name\":null,\"position\":null}}. Use \"ALL\" in tags if everything is wanted. Question: {q}"
        payload = json.dumps({"model": names[0], "messages": [{"role": "user", "content": prompt}], "stream": False}).encode()
        req = urllib.request.Request("http://localhost:11434/api/chat", data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            return _parse_json(json.loads(r.read().decode())['message']['content'])
    except Exception:
        return None

def keyword_fallback(q):
    q = q.lower(); tags = []
    if 'today' in q: tags.append('interview today')
    if 'tomorrow' in q: tags.append('interview tomorrow')
    if 'scheduled' in q or 'upcoming' in q or 'later' in q: tags.append('interview scheduled')
    if 'call' in q: tags.append('call scheduled')
    if 'feedback' in q: tags.append('feedback pending')
    if 'review' in q: tags.append('ready for manager review')
    if 'update' in q: tags.append('awaiting cv update')
    if 'jd' in q or 'ack' in q: tags.append('awaiting jd confirmation')
    if 'cleared' in q: tags.append('interview cleared')
    if 'join' in q: tags.append('expected to join')
    if 'payment' in q: tags += ['joined - payment pending', 'payment received']
    if 'closed' in q or 'reject' in q: tags += ['closed - not proceeding', 'rejected by client']
    return {'tags': tags or [k for k, _, _ in TAGS], 'name': None, 'position': None}

def _company_root(root):
    lr = os.path.expanduser('~/.cvtool_company_root')
    if os.path.exists(lr):
        v = open(lr).read().strip()
        if os.path.isdir(v): return v
    r = os.path.abspath(root)
    while r != os.path.dirname(r):
        if re.match(r'^\d+', os.path.basename(r)): return os.path.dirname(r)
        r = os.path.dirname(r)
    return os.path.abspath(root)

def _pick_model(names):
    for pref in ('7b', '8b', '14b', '32b'):
        for n in names:
            if pref in n: return n
    return names[0]

SYS_BUTLER = ("You are Butler, recruitment assistant of Sundeep Rana (Sunsoft Technology). "
              "Answer briefly and practically using CONTEXT and COMMAND CARD. If the user wants an ACTION, "
              "give the exact command (e.g. 'wa pradip <your words>', 'missed pradip', 'focus avis'). "
              "If it is not in CONTEXT and not general knowledge, say you don't know.")

def ask_ollama_stream(messages, say=print):
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as r:
            names = [m['name'] for m in json.loads(r.read().decode()).get('models', []) if 'embed' not in m['name'].lower()]
        if not names: return False
        payload = json.dumps({"model": _pick_model(names), "messages": messages, "stream": True}).encode()
        req = urllib.request.Request("http://localhost:11434/api/chat", data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            for line in r:
                try: d = json.loads(line)
                except Exception: continue
                tok = (d.get('message') or {}).get('content') or ''
                if tok: print(tok, end='', flush=True)
        print()
        return True
    except Exception:
        return False

def build_context(root, q):
    parts = []
    try:
        data = collect(root)
        counts = {k: len(v) for k, v in data.items() if v}
        if counts: parts.append("PIPELINE NOW: " + ", ".join(f"{k}={n}" for k, n in counts.items()))
    except Exception: pass
    f = _read_focus()
    if f: parts.append(f"FOCUS: {f['client']} - {f['display']}")
    try:
        for h in _hits_for(q, root)[:2]:
            try:
                import pdfplumber
                with pdfplumber.open(h) as pdf: txt = (pdf.pages[0].extract_text() or '')[:1200]
            except Exception: txt = ''
            parts.append(f"CANDIDATE: {os.path.relpath(h, root)} | phone: {phone_of(h) or '?'}\nFIRST PAGE:\n{txt}")
    except Exception: pass
    return "\n\n".join(parts)

def _local_name(q):
    stop = {'the','a','an','in','on','for','to','is','are','was','were','my','your','our','their','today','tomorrow','all','any','please','call','calls','called','message','whatsapp','text','send','summarize','summarise','draft','why','how','who','what','when','where','about','tell','me','him','her','them','candidate','candidates'}
    toks = [t.strip('.,!?') for t in q.split() if t.strip('.,!?')[:1].isupper() and t.strip('.,!?').lower() not in stop]
    return ' '.join(toks[:3]) if toks else ''

EAR_WORDS = ('said', 'will', 'send', 'sent', 'missed', 'not interested', 'ready', 'update', 'acknowledge', 'confirm', 'joined', 'interview', 'feedback', 'pick', 'answer')  # EAR v84.35: an event-word or it is not an ear-sentence
EAR_TAGS = [('not interested', 'Closed \u2013 Not Proceeding'), ('rejected by client', 'Rejected by Client'), ('ready for manager', 'Ready for Manager Review'), ('manager review', 'Ready for Manager Review'), ('will send cv', 'Awaiting CV Update'), ('send the cv', 'Awaiting CV Update'), ('update cv', 'Awaiting CV Update'), ('updated cv', 'Awaiting CV Update'), ('missed', 'Call Scheduled'), ('no answer', 'Call Scheduled'), ('didn\u2019t pick', 'Call Scheduled'), ('did not pick', 'Call Scheduled'), ('jd mailed', 'Awaiting JD Confirmation'), ('acknowledge', 'Awaiting JD Confirmation'), ('interested', 'Awaiting JD Confirmation'), ('feedback pending', 'Feedback Pending'), ('interview tomorrow', 'Interview Tomorrow'), ('interview today', 'Interview Today'), ('interview', 'Interview Scheduled'), ('joined', 'Expected to Join'), ('call scheduled', 'Call Scheduled')]  # EAR v84.35: the deterministic table speaks first
def _ear_json(q, vocab):  # EAR-JSON v84.35: the brain answers the ear in grammar, not prose; offline it is silent
    try:
        with urllib.request.urlopen('http://localhost:11434/api/tags', timeout=5) as r:
            names = [m['name'] for m in json.loads(r.read().decode()).get('models', []) if 'embed' not in m['name'].lower()]
        if not names: return None
        payload = json.dumps({'model': names[0], 'messages': [{'role': 'user', 'content': f'From this recruiter sentence return ONLY JSON like {{"tag": "<one of: {vocab}>"}} or {{"tag": null}}. Sentence: {q}'}], 'stream': False}).encode()
        req = urllib.request.Request('http://localhost:11434/api/chat', data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=60) as r:
            d = _parse_json(json.loads(r.read().decode())['message']['content'])
        return (d or {}).get('tag')
    except Exception:
        return None
def _ear_intent(q, root, say=print):  # EAR v84.35: a sentence about a human becomes a proposal; the thumb still executes
    ql = (q or '').lower()
    if not any(w in ql for w in EAR_WORDS): return False
    import butler as _bt
    nm = _name_from(q) or _local_name(q)
    p = None
    if nm:
        hs = _hits_for(nm, root)
        if len(hs) == 1: p = hs[0]
    if p is None and _bt.sheet_current():
        p = _bt.sheet_current()['p']; nm = nm or os.path.splitext(os.path.basename(p))[0]
    if not p: return False
    tag = next((t for w, t in EAR_TAGS if w in ql), None)
    if not tag: tag = _ear_json(q, ' / '.join(_bt._tag_vocab()))
    if not tag or tag not in _bt._tag_vocab(): return False
    on = not any(w in ql for w in ('remove', 'undo', 'off', 'cancel'))
    say(f'🤖 Proposal: {os.path.splitext(os.path.basename(p))[0]} → [{tag}] (heard from your sentence) · y / n')
    try:
        json.dump({'p': p, 'tag': tag, 'on': on, 'move_to': True}, open(os.path.join(BASE_DIR, 'pending_action.json'), 'w'))
    except Exception:
        return False
    say('· proposal waiting - type y or n on the next line')
    return True

def answer(root, q, say=print):
    if _ear_intent(q, root, say): return  # EAR v84.35: a sentence about a human becomes a proposal before the brain wanders
    ql = q.lower()
    kb = keyword_fallback(q)
    talk_words = ('why', 'how', 'summar', 'explain', 'draft', 'should', 'compare', 'message', 'whatsapp', 'about', 'tell', 'can we', 'what do', 'who is')
    list_like = any(w in ql for w in ('today', 'tomorrow', 'scheduled', 'call', 'feedback', 'review', 'update', 'pending'))
    shown = 0
    if list_like:
        data = collect(root)
        nm = _local_name(q).lower()
        for k, title, note in TAGS:
            if k not in kb['tags']: continue
            items = data[k]
            if nm: items = [i for i in items if nm in i[0].lower()]
            shown += render(say, title, items, note)
        if shown and not any(w in ql for w in talk_words):
            return
    if not shown:
        say("   🤷 no pipeline rows match.")
    say("   🧠 thinking…", flush=True)
    msgs = [{"role": "system", "content": SYS_BUTLER},
            {"role": "user", "content": f"CONTEXT:\n{build_context(root, q)}\n\nCOMMAND CARD:\n{HELP_CARD}\n\nQUESTION: {q}"}]
    if not ask_ollama_stream(msgs, say):
        say("   (Ollama offline - pipeline data above is all I have)")
# ---------- workflow: focus + missed-call WhatsApp ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FOCUS_FILE = os.path.join(BASE_DIR, "focus.json")
TPL_FILE = os.path.join(BASE_DIR, "wa_template.txt")
DEFAULT_TPL = ("Hi {name}, Sundeep Rana here from Sunsoft Technology. 📞\n"
"I tried calling you today regarding the {position} role at {where}, but couldn't reach you.\n"
"Kindly share your updated CV in PDF format here, along with a good time to reconnect. 🙏\n"
"Regards,\nSundeep Rana")

def _read_tpl():
    if not os.path.exists(TPL_FILE):
        with open(TPL_FILE, 'w') as f: f.write(DEFAULT_TPL)
    return open(TPL_FILE).read().strip()

def _read_focus():
    try: return json.load(open(FOCUS_FILE))
    except Exception: return None

WATCH_PID = os.path.join(BASE_DIR, "watch.pid")
WATCH_LOG = os.path.join(BASE_DIR, "butler_focus.log")

def _lock_pid(root):
    import hashlib
    lp = os.path.join(BASE_DIR, "butler_" + hashlib.md5(os.path.abspath(root).encode()).hexdigest()[:8] + ".lock")
    try:
        pid = int(open(lp).read().split('|')[0].strip())
        os.kill(pid, 0)
        return pid
    except Exception:
        return None

def _stop_watch(say=print):
    import subprocess as _sp
    try:
        for t in open(WATCH_PID).read().split():
            pid = int(t)
            try:
                cmd = _sp.run(['ps', '-p', str(pid), '-o', 'command='], capture_output=True, text=True, timeout=5).stdout
                if 'butler.py' not in cmd:
                    continue   # stale or recycled PID: never kill strangers
                os.kill(pid, 15); say(f"   ⏹ stopped watcher (pid {pid})")
            except Exception: pass
    except Exception:
        pass
    try: os.remove(WATCH_PID)
    except Exception: pass

def _watch_covered(root):
    a = os.path.abspath(root)
    for fn2 in os.listdir(BASE_DIR):
        if not (fn2.startswith('butler_') and fn2.endswith('.lock')): continue
        lp = os.path.join(BASE_DIR, fn2)
        try:
            parts = open(lp).read().strip().split('|')
            pid = int(parts[0]); os.kill(pid, 0)
            other = os.path.abspath(parts[1]) if len(parts) > 1 else None
        except Exception:
            continue
        if other and other != a and (a.startswith(other + os.sep) or other.startswith(a + os.sep)):
            return other
    return None

def _start_watch(root, say=print):
    import subprocess, time
    if _lock_pid(root):
        say(f"   🤖 {os.path.basename(root)}: already watched by a running butler")
        return None
    cov = _watch_covered(root)
    if cov:
        say(f"   🤖 {os.path.basename(root)}: already covered by butler watching {os.path.basename(cov)}")
        return None
    lf = open(WATCH_LOG, 'ab')
    pr = subprocess.Popen([sys.executable, os.path.join(BASE_DIR, 'butler.py'), root],
                          stdout=lf, stderr=lf, start_new_session=True, cwd=BASE_DIR)
    time.sleep(2)
    if pr.poll() is None:
        say(f"   🤖 butler now watching: {os.path.basename(root)} (log: butler_focus.log)")
        return pr.pid
    say(f"   ⚠️ watcher for {os.path.basename(root)} did not stay up")
    return None

def do_focus(arg, root, say=print):
    arg = (arg or '').strip()
    if not arg:
        f = _read_focus()
        if f:
            say(f"🎯 focus: {f['client']} · {f['display']}")
            for x in f.get('also', []):
                say(f"   + {x['client']} · {x['display']}")
        else:
            say("🎯 no focus set")
        try:
            pids = [int(t) for t in open(WATCH_PID).read().split()]
            alive = 0
            for p in pids:
                try: os.kill(p, 0); alive += 1
                except Exception: pass
            say(f"   🤖 watchers running: {alive}")
        except Exception:
            say("   🤖 watcher: not running")
        return
    if arg.lower() == 'clear':
        try: os.remove(FOCUS_FILE)
        except Exception: pass
        _stop_watch(say)
        say("🎯 focus cleared"); return
    picks = []
    for part in [x.strip() for x in arg.split(',') if x.strip()]:
        words = [w for w in part.lower().split() if len(w) > 2]
        hits = []
        for dp, dn, fn in os.walk(root):
            if os.path.abspath(dp) == os.path.abspath(root): continue
            bl = os.path.basename(dp).lower()
            if bl.startswith('.') or bl in FOCUS_SKIP: continue
            if os.path.dirname(dp) == os.path.abspath(root): continue  # clients are not positions
            if any(w in bl for w in words):
                hits.append(dp)
        if not hits:
            for dp, dn, fn in os.walk(root):   # matched a client? offer ALL its positions
                if os.path.dirname(dp) == os.path.abspath(root) and any(w in os.path.basename(dp).lower() for w in words):
                    for sub in dn:
                        sb = sub.lower()
                        if sb.startswith('.') or sb in FOCUS_SKIP: continue
                        hits.append(os.path.join(dp, sub))
        if not hits:
            say(f"🤷 no position folder matches '{part}'"); continue
        if len(hits) > 1:
            for i, h in enumerate(hits): say(f"   {i+1}) {os.path.relpath(h, root)}")
            raw = input("   pick # (comma for several, 'all' for every): ").strip()
            sel = list(hits) if raw.lower() in ('all', 'a') else []
            if raw.lower() not in ('all', 'a'):
                for t in raw.split(','):
                    try: sel.append(hits[int(t.strip()) - 1])
                    except Exception: pass
            if not sel: return
        else:
            sel = [hits[0]]
        for pick in sel:
            client = re.sub(r'^\d+[\s_-]*', '', os.path.basename(os.path.dirname(pick)))
            picks.append({'path': pick, 'display': clean_pos(os.path.basename(pick)), 'client': client})
    if not picks:
        return
    data = dict(picks[0])
    data['also'] = picks[1:]
    json.dump(data, open(FOCUS_FILE, 'w'), indent=2)
    say(f"🎯 focused (saved): {data['client']} · {data['display']}" + (f"  +{len(data['also'])} more" if data['also'] else ""))
    _stop_watch(say)
    pids = []
    seen = set()
    for pos in picks:
        r = os.path.dirname(pos['path'])
        if r in seen: continue
        seen.add(r)
        pid = _start_watch(r, say)
        if pid: pids.append(pid)
    if pids:
        with open(WATCH_PID, 'w') as f: f.write("\n".join(str(x) for x in pids))

def _full_name(path):
    b = os.path.splitext(os.path.basename(path))[0]
    b = re.sub(r'[\s_(-]*\d+[)\s_]*$', '', b).strip()
    return b or os.path.splitext(os.path.basename(path))[0]

def _idx_path(root):
    import hashlib
    return os.path.join(BASE_DIR, 'scan_index_' + hashlib.md5(os.path.abspath(root).encode()).hexdigest()[:8] + '.json')

def _phones_by_basename(p):
    try:
        dd = json.load(open(PHONES_FILE)) if os.path.exists(PHONES_FILE) else {}
    except Exception:
        return []
    b = os.path.basename(p).lower()
    for k, v in dd.items():
        if os.path.basename(k).lower() == b: return v.get('phones') or []
    return []

def _phone_first(arg):
    m = re.match(r'^\s*(\d{10}|\d{12})\b\s*(.*)$', arg or '', re.S)
    if not m: return None, arg
    d = m.group(1)
    if len(d) == 10: d = '91' + d
    return d, m.group(2).strip()

def _scan_path(num, root=None):
    base = os.path.dirname(os.path.abspath(__file__))
    names = []
    if root:
        names.append('scan_index_' + hashlib.md5(os.path.abspath(root).encode()).hexdigest()[:8] + '.json')
    for fn in names + sorted(x for x in os.listdir(base) if x.startswith('scan_index_') and x.endswith('.json')):
        try: d = json.load(open(os.path.join(base, fn)))
        except Exception: continue
        if root and os.path.abspath(d.get('root') or '') != os.path.abspath(root): continue
        hit = (d.get('idx') or {}).get(str(num))
        if hit and os.path.exists(hit): return hit
    return None
def do_history(arg, root, say=print):
    from butler import StageLog
    if not arg: say('usage: history <name>'); return
    slog = StageLog(root)
    rows = slog.all_for(arg)
    if not rows: say(f'no history for {arg!r}'); return
    say(f"{arg}:")
    import datetime as _dt
    for r in rows:
        d = _dt.datetime.fromtimestamp(r['ts']).strftime('%Y-%m-%d')
        say(f"  {d} · {r['stage']} · {r.get('position','')}")
def do_stale(arg, root, say=print):
    from butler import StageLog
    days = int(arg) if (arg or '').strip().isdigit() else 7
    slog = StageLog(root)
    now = int(time.time())
    out = []
    for k, entries in slog.data.items():
        if not entries: continue
        last = entries[-1]
        age = (now - last['ts']) // 86400
        if age >= days:
            out.append((age, k.title(), last['stage'], last.get('position','')))
    if not out: say(f'nothing older than {days}d'); return
    say(f'🕑 stale (>{days}d):')
    for age, nm, st, ps in sorted(out, reverse=True):
        say(f'  {age:3d}d · {nm:<24s} · {st} · {ps}')

def do_fixphone(arg, root, say=print):
    parts = (arg or '').split()
    if len(parts) < 2: say('usage: fixphone <name or scan#> <10-digit phone>'); return
    num = re.sub(r'\D', '', parts[-1])
    if len(num) == 10: num = '91' + num
    who = ' '.join(parts[:-1])
    path = None
    if who.isdigit():
        path = _scan_path(int(who), root)
    else:
        d0 = json.load(open(PHONES_FILE)) if os.path.exists(PHONES_FILE) else {}
        c = [k for k in d0 if os.path.basename(k).lower().startswith(who.lower())]
        if not c:
            c = [os.path.join(dp, f) for dp, dn, fn in os.walk(root) for f in fn if f.lower().startswith(who.lower().rstrip('.'))][:1]
        path = c[0] if c else None
    if not path: say(f'no candidate for {who!r}'); return
    d = json.load(open(PHONES_FILE)) if os.path.exists(PHONES_FILE) else {}
    e = d.setdefault(path, {'k': '', 'phones': []})
    e['phones'] = [num]
    json.dump(d, open(PHONES_FILE, 'w'), indent=2)
    say(f"📞 learned: {os.path.basename(path)} -> +{num} (overrides PDF from now on)")

def _stage_words(who):
    import ledger
    nm = os.path.splitext(os.path.basename(who))[0].lower() if str(who).lower().endswith('.pdf') else re.sub(r'[^a-z]', ' ', str(who).lower()).strip()
    cs = ledger._load(ledger.CASES).get(nm.replace(' ', ''), {}) or ledger._load(ledger.CASES).get(nm, {})
    sts = cs.get('stages') or []
    st = (sts[0].get('stage') or '').lower() if sts else ''
    if not st:
        try:
            conv = json.load(open(os.path.join(BASE_DIR, 'conversations.json')))
            for p in (cs.get('phones') or []):
                e = conv.get(re.sub(r'\D', '', str(p)))
                if not e: continue
                outs = [m['text'].lower() for m in e.get('messages', []) if m['dir'] == 'out']
                if outs and any('not relevant' in t for t in outs[-3:]): return ['rejected']
        except Exception:
            pass
        return None
    if 'closed' in st: return ['referral']
    if 'rejected' in st: return ['rejected']
    if 'awaiting jd' in st: return ['awaiting']
    if 'interview' in st and 'cleared' not in st: return ['interview']
    if 'cleared' in st or 'join' in st or 'payment' in st: return ['feedback']
    if 'feedback pending' in st or 'ready for manager' in st or 'awaiting cv' in st: return ['outbox']
    if 'call scheduled' in st: return ['missed']
    return None
def _tpl_name(words):
    words = words or ['missed']
    try:
        for f in sorted(os.listdir(TPL_DIR)):
            stem = os.path.splitext(f)[0].lower()
            if any(w in stem or stem in w for w in words): return stem
    except Exception: pass
    return 'awaiting (fallback)'

def do_desk(arg, root, say=print):  # DESK v84.0
    butler.desk_cmd(arg, root, say)
def do_briefing(arg, root, say=print):  # BRIEFING v84.0
    butler.daily_briefing(say)
def do_confirm(arg, root, say=print):  # PROPOSE-FIRST v84.4
    butler.action_execute(say)
def do_cancel(arg, root, say=print):  # PROPOSE-FIRST v84.4
    butler.action_cancel(say)

def do_dash(arg, root, say=print):  # DASH v84.7
    butler.desk_dashboard(say)
def do_calls(arg, root, say=print):  # CHAIR v84.10b
    butler.calls_cmd(arg, root, say)
def do_sheet(arg, root, say=print):  # CHAIR v84.10b
    butler.sheet_cmd(arg, root, say)
def do_up(arg, root, say=print):  # CHAIR v84.10b
    butler.up_cmd(arg, root, say)
def do_outcome(arg, root, say=print):  # CHAIR v84.10b
    butler.outcome_cmd(arg, root, say)

def do_tidy(arg, root, say=print):  # TIDY v84.9
    butler.tags_tidy(say)

def do_audit(arg, root, say=print):  # AUDIT v84.7
    butler.tags_audit(say)

def do_tagcmd(arg, root, say=print):  # TAG-VOICE v84.2c: the whole sentence goes to the clerk; the tag is read from its tail
    if arg.startswith('off '): butler.tag_voice(arg[4:], False, say); return
    butler.tag_voice(arg, True, say)


def do_chase(arg, root, say=print):  # CHASE v84.0
    butler.chase_cmd(arg, root, say)

def do_pending(arg, root, say=print):
    butler.pipeline_pending(arg or None, say)
def do_status(arg, root, say=print):
    butler.pipeline_status(arg, say)
def do_note(arg, root, say=print):
    parts = arg.split(' ', 1)
    if len(parts) < 2: say('usage: note <name> <text>'); return
    butler.pipeline_note(parts[0], parts[1], say)

def do_missed(arg, root, say=print, ask=None, words=None):
    arg = (arg or '').strip()
    f = _read_focus()
    if not f:
        f = {'path': root, 'display': clean_pos(os.path.basename(root)),
             'client': re.sub(r'^\d+[\s_-]*', '', os.path.basename(os.path.dirname(root)))}
    ph0, rest0 = _phone_first(arg)
    if ph0:
        nm = rest0.title() or 'there'
        pos, cli = _pos_client_for(None, f)
        cli = f['client'] if f else re.sub(r'^\d+[\s_-]*', '', os.path.basename(os.path.dirname(root)))
        text = _fmt_tpl(_tpl_for(words or ['missed']), None, f, nm)
        try:
            import wa
            wa.send_review(ph0, text, say, ask=ask)
        except Exception as e:
            say(f"⚠️ whatsapp failed: {e}")
        return
    q = arg.lower().strip()
    hit = _scan_path(arg.strip(), root) if arg.strip().isdigit() else None
    if arg.strip().isdigit() and not hit:
        say(f"🤷 no file at scan number {arg.strip()} in the latest scan"); return
    _cr = os.path.dirname(os.path.dirname(f['path']))  # WORKSPACE-CLAMP v81.82: the butler's world is the workspace root; nothing above it is ever walked
    _roots = [f['path']] + ([_cr] if (_cr.startswith(root) and _cr != f['path']) else [])
    _qt = [t for t in q.split()]  # STRICT-RESOLVE v81.75: exact stem, equal token-sets, or whole words only; several humans means a question, never a guess
    _strict = []
    for _sr2 in _roots:
        for dp, dn, fn in os.walk(_sr2):
            for x in fn:
                if not x.lower().endswith('.pdf'): continue
                _xs = os.path.splitext(x)[0].lower().replace('_', ' ')
                if _xs == q or sorted(_xs.split()) == sorted(_qt) or all(t in _xs.split() for t in _qt):
                    _p = os.path.join(dp, x)
                    if _p not in _strict: _strict.append(_p)  # DEDUPE v81.79: the client walk contains the position walk; a human is listed once
    if len(_strict) == 1:
        hit = _strict[0]
    elif len(_strict) > 1:
        try:  # PICK-GRACEFUL-WIDE v81.82: Ctrl-C anywhere in the picker - listing or prompt - is a choice, not a crash
            say('🪪 several candidates wear that name - pick the human by email:')
            for _n, _c in enumerate(_strict, 1):
                try: _em = (butler.emails_of(_c) or ['none readable'])[0]
                except Exception: _em = 'none readable'
                try: _ph = (butler.phones_of(_c, quiet=True) or ['none readable'])[0]  # PHONE-IN-PICKER v81.87: the row shows the number too, so the master verifies who AND where at one glance
                except Exception: _ph = 'none readable'
                say(f'   {_n}) {os.path.basename(_c)} · {_em} · {_ph} · {os.path.relpath(os.path.dirname(_c), root)}')    # POSITION-LABEL v81.76 # PATH-LABEL v81.79: the whole folder trail from the client down - position and stage together - because that is what tells humans apart (comment lives outside the f-string braces)
            hit = _strict[int(input('   pick #: ').strip()) - 1]  # the inner try becomes a plain assignment: the outer embrace owns both excepts
        except KeyboardInterrupt: say('👋 pick cancelled - nothing drafted'); hit = None  # PICK-GRACEFUL v81.81: Ctrl-C at the picker is a choice, not a crash
        except Exception: say('🤷 pick skipped'); hit = None

    for _sr in ([] if hit else _roots):
        for dp, dn, fn in os.walk(_sr):
            for x in fn:
                if x.lower().endswith('.pdf') and all(t in os.path.splitext(x)[0].lower().replace('_', ' ').split() for t in q.split()):  # WHOLE-WORD-WALK v81.81: the loose walk stops guessing by substring; a token is a whole word or the candidate is not offered
                    hit = os.path.join(dp, x); break
            if hit: break
        if hit: break
    if not hit:
        say(f"🤷 no candidate like '{arg}' under {f['display']}"); return
    if words == 'AUTO': words = _stage_words(hit) or ['outbox']
    elif words: words = _stage_words(hit) or words
    say(f'   🗣 voice: {_tpl_name(words)}')
    phone = _pick_phone(_phones_by_basename(hit) or phones_of(hit), say, path=hit)
    if not phone:
        say("🤷 no phone found in that CV"); return
    name = _full_name(hit)
    text = _fmt_tpl(_tpl_for(words or ['missed']), hit, f, name)
    try:
        import wa
        wa.send_review(phone, text, say, ask=ask)
        try: import fitrank; fitrank.mark_called(hit)
        except Exception: pass
    except Exception as e:
        say(f"⚠️ whatsapp failed: {e}")

TPL_DIR = os.path.join(BASE_DIR, "templates")

def _tpl_for(words):
    SYN = {'nudge': 'awaiting', 'reminder': 'awaiting', 'followup': 'outbox', 'follow': 'outbox', 'chase': 'outbox', 'goodluck': 'interview', 'wish': 'interview', 'fb': 'feedback'}
    words = list(words) + [SYN[w] for w in words if w in SYN]
    os.makedirs(TPL_DIR, exist_ok=True)
    for f in sorted(os.listdir(TPL_DIR)):
        stem = os.path.splitext(f)[0].lower()
        if any(w in stem or stem in w for w in words):
            return open(os.path.join(TPL_DIR, f)).read().strip()
    p = os.path.join(TPL_DIR, 'awaiting.txt')
    return open(p).read().strip() if os.path.exists(p) else _read_tpl()

def do_reject(arg, root, say=print, ask=None):
    f = _read_focus()
    if not f:
        say("set a focus first:  focus <position words>"); return
    q = arg.lower().strip()
    if not q:
        say("usage: reject <candidate name>"); return
    hit = _scan_path(arg.strip(), root) if arg.strip().isdigit() else None
    if arg.strip().isdigit() and not hit:
        say(f"🤷 no file at scan number {arg.strip()} in the latest scan"); return
    for dp, dn, fn in ([] if hit else os.walk(f['path'])):
        for x in fn:
            if x.lower().endswith('.pdf') and all(t in x.lower() for t in q.split() if len(t) > 2):
                hit = os.path.join(dp, x); break
        if hit: break
    if not hit:
        say(f"🤷 no candidate like '{arg}' under {f['display']}"); return
    phone = _pick_phone(_phones_by_basename(hit) or phones_of(hit), say, path=hit)
    if not phone:
        say("🤷 no phone found in that CV"); return
    name = _full_name(hit)
    tpl = _tpl_for(['rejected'])
    try:
        text = _fmt_tpl(tpl, hit, f, name)
    except Exception:
        text = tpl
    try:
        import wa
        wa.send_review(phone, text, say, ask=ask)
        try: import fitrank; fitrank.mark_called(hit)
        except Exception: pass
    except Exception as e:
        say(f"⚠️ whatsapp failed: {e}")

def do_send(arg, root, tpl_words, say=print, ask=None):
    arg = (arg or '').strip()
    f = _read_focus()
    base = f['path'] if f else root
    ph0, rest0 = _phone_first(arg)
    if ph0:
        nm = rest0.title() or 'there'
        pos, cli = _pos_client_for(None, f)
        cli = f['client'] if f else re.sub(r'^\d+[\s_-]*', '', os.path.basename(os.path.dirname(root)))
        text = _fmt_tpl(_tpl_for(tpl_words), None, f, nm)
        try:
            import wa
            wa.send_review(ph0, text, say, ask=ask)
        except Exception as e:
            say(f"⚠️ whatsapp failed: {e}")
        return
    q = arg.lower().strip()
    if not q:
        say("usage: <command> <candidate name>"); return
    hit = _scan_path(arg.strip(), root) if arg.strip().isdigit() else None
    if arg.strip().isdigit() and not hit:
        say(f"🤷 no file at scan number {arg.strip()} in the latest scan"); return
    for scan_root in ([] if hit else (base, root)):
        for dp, dn, fnames in os.walk(scan_root):
            for x in fnames:
                if x.lower().endswith('.pdf') and all(t in x.lower() for t in q.split() if len(t) > 2):
                    hit = os.path.join(dp, x); break
            if hit: break
        if hit: break
    if not hit:
        say(f"🤷 no candidate like '{arg}'"); return
    phone = _pick_phone(_phones_by_basename(hit) or phones_of(hit), say, path=hit)
    if not phone:
        say("🤷 no phone found in that CV"); return
    nm = _full_name(hit)
    say(f'   🗣 voice: {_tpl_name(tpl_words)}')
    pos, cli = _pos_client_for(None, f)
    cli = f['client'] if f else re.sub(r'^\d+[\s_-]*', '', os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(hit)))))
    tpl = _tpl_for(tpl_words)
    try:
        text = _fmt_tpl(tpl, hit, f, nm)
    except Exception:
        text = tpl
    try:
        import wa
        wa.send_review(phone, text, say, ask=ask)
        try: import fitrank; fitrank.mark_called(hit)
        except Exception: pass
    except Exception as e:
        say(f"⚠️ whatsapp failed: {e}")

def do_name(arg, root, say=print):
    if '=' not in arg:
        say("usage: name <file words> = <Correct Name>"); return
    q, correct = [x.strip() for x in arg.split('=', 1)]
    if not q or not correct:
        say("usage: name <file words> = <Correct Name>"); return
    f = _read_focus(); base = (f or {}).get('path') or root
    hit = None
    for scan_root in (base, root):
        for dp, dn, fnames in os.walk(scan_root):
            for x in fnames:
                if x.lower().endswith('.pdf') and all(t in x.lower() for t in q.lower().split() if len(t) > 2):
                    hit = os.path.join(dp, x); break
            if hit: break
        if hit: break
    if not hit:
        say(f"🤷 no PDF matches '{q}'"); return
    d = os.path.dirname(hit); ob = os.path.basename(hit)
    target = os.path.join(d, correct + '.pdf'); c = 1
    while os.path.exists(target): target = os.path.join(d, f"{correct}_{c}.pdf"); c += 1
    os.rename(hit, target)
    try:
        lk = os.path.join(BASE_DIR, 'name_locks.json')
        locks = json.load(open(lk)) if os.path.exists(lk) else []
        locks.append(os.path.basename(target)); json.dump(locks, open(lk, 'w'), indent=2)
    except Exception: pass
    try:
        import butler as _b
        _b.learn_name(correct, correct)
    except Exception: pass
    say(f"✅ named + locked: {os.path.basename(target)} (butler will never fight this name; future readable copies auto-learn it)")

def do_text(arg, root, say=print, ask=None):
    words = [w for w in arg.lower().split() if len(w) > 2]
    if not words:
        say("usage: text <tag words>   e.g.  text rejected by client"); return
    base = (_read_focus() or {}).get('path') or root
    hits = []
    for dp, dn, fn in os.walk(base):
        bn = os.path.basename(dp).lower()
        pb = os.path.basename(os.path.dirname(dp)).lower()
        if pb.startswith('jd') and any(w in bn for w in words):
            hits.append(dp)
    if not hits:
        say("🤷 no tag folder matches under the current focus"); return
    tpl = _tpl_for(words)
    for folder in hits:
        pos = clean_pos(os.path.basename(os.path.dirname(folder)))
        client = _client_full(os.path.basename(os.path.dirname(os.path.dirname(folder))), os.path.dirname(os.path.dirname(folder)))
        pdfs = [x for x in sorted(os.listdir(folder)) if x.lower().endswith('.pdf')]
        say(f"\n📨 {os.path.basename(folder)} - {len(pdfs)} candidate(s), one by one:")
        for x in pdfs:
            name = _full_name(os.path.join(folder, x))
            phone = phone_of(os.path.join(folder, x))
            if not phone:
                say(f"   ⚠️ {name}: no phone in CV - skipped"); continue
            try:
                text = _fmt_tpl(tpl, os.path.join(folder, x), f, name)
            except Exception:
                text = tpl
            try:
                import wa
                wa.send_review(phone, text, say, ask=ask)
                try: import fitrank; fitrank.mark_called(os.path.join(folder, x))
                except Exception: pass
            except KeyboardInterrupt:
                say("\n⏹ stopped - the rest stay untouched"); return
            except Exception as e:
                say(f"⚠️ whatsapp failed: {e}")

def _ai_name(q):
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as r:
            names = [m['name'] for m in json.loads(r.read().decode()).get('models', []) if 'embed' not in m['name'].lower()]
        if not names: return None
        payload = json.dumps({"model": names[0], "messages": [{"role": "user", "content": f'From this sentence return ONLY JSON like {{"name": "Full Name"}} or {{"name": null}}. Sentence: {q}'}], "stream": False}).encode()
        req = urllib.request.Request("http://localhost:11434/api/chat", data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            d = _parse_json(json.loads(r.read().decode())['message']['content'])
        return (d or {}).get('name')
    except Exception:
        return None

def _name_from(q):
    nm = _ai_name(q)
    if nm and 2 <= len(str(nm).split()) <= 4: return str(nm)
    stop = {'said','call','me','later','can','you','to','that','the','a','in','on','for','please','today','tomorrow','folder','where','is','which','take','whatsapp','she','he','will','and','her','him','i','my'}
    toks = [t.strip('.,!?') for t in q.split() if t.strip('.,!?')[:1].isupper() and t.strip('.,!?').lower() not in stop]
    return ' '.join(toks[:4]) if toks else None

def do_where(arg, root, say=print):
    q = arg.lower().strip()
    if not q:
        say("usage: where <candidate name>"); return
    hits = []
    for dp, dn, fnames in os.walk(root):
        for f in fnames:
            if f.lower().endswith('.pdf') and all(t in f.lower() for t in q.split() if len(t) > 2):
                hits.append(os.path.join(dp, f))
    if not hits:
        say(f"🤷 no file matches '{arg}' anywhere under {os.path.basename(root)}")
        return
    for h in hits:
        say(f"📍 {os.path.relpath(h, root)}")
    import subprocess
    subprocess.run(['open', '-R', hits[0]])
    if len(hits) > 1:
        say(f"   (+{len(hits)-1} more copy/ies listed above - revealed the first)")

def do_update(arg, root, say=print):
    import datetime as _dt
    f = _read_focus()
    base = (f or {}).get('path') or root
    q = arg.lower().strip()
    if not q:
        say("usage: update <candidate name>"); return
    skip = ('previous versions', 'duplicates', 'converted doc files', 'converted files')
    hits = []
    for dp, dn, fnames in os.walk(base):
        dn[:] = [d for d in dn if d.lower() not in skip]
        for x in fnames:
            if x.lower().endswith(('.pdf', '.docx', '.doc')) and all(t in x.lower() for t in q.split() if len(t) > 2):
                hits.append(os.path.join(dp, x))
    if len(hits) < 2:
        say(f"🤷 found {len(hits)} file(s) for '{arg}' - need old + new in the tree"); return
    hits.sort(key=lambda x: os.path.getmtime(x))
    old, new = hits[0], hits[-1]
    fmt = lambda x: _dt.datetime.fromtimestamp(os.path.getmtime(x)).strftime('%d %b %Y %H:%M')
    say(f"📄 old: {os.path.relpath(old, base)}  ({fmt(old)})")
    say(f"📄 new: {os.path.relpath(new, base)}  ({fmt(new)})")
    cb = os.path.splitext(os.path.basename(old))[0]
    ext = os.path.splitext(new)[1]
    say(f"plan: NEW becomes '{cb}{ext}' · OLD parked in Previous Versions/ (never deleted)")
    try:
        r = input("   [Enter] do it · [q] skip: ").strip().lower()
    except EOFError:
        r = 'q'
    if r:
        say("skipped"); return
    pv = os.path.join(os.path.dirname(old), 'Previous Versions')
    os.makedirs(pv, exist_ok=True)
    dest = os.path.join(pv, f"{cb} (until {_dt.datetime.now().strftime('%Y%m%d')}){os.path.splitext(old)[1]}")
    os.rename(old, dest)
    target = os.path.join(os.path.dirname(old), f"{cb}{ext}")
    c = 1
    while os.path.exists(target):
        target = os.path.join(os.path.dirname(old), f"{cb}_{c}{ext}"); c += 1
    os.rename(new, target)
    say(f"✅ updated: {os.path.basename(target)} · old copy safe in Previous Versions/")

def do_log(n=25):
    lp = os.path.join(BASE_DIR, 'butler_live.log')
    try:
        lines = open(lp, errors='ignore').read().splitlines()
        for l in lines[-max(5, int(n)):] :
            print(l)
    except Exception:
        print("   (no live log yet - use: start <folder>)")

def do_start(arg, say=print):
    import subprocess
    lr = os.path.expanduser('~/.cvtool_last_root')
    root = arg.strip()
    if not root and os.path.exists(lr):
        root = open(lr).read().strip()
    if not root:
        say("usage: start <folder>"); return
    subprocess.run(['pkill', '-f', 'butler.py'], capture_output=True)
    lg = open(os.path.join(BASE_DIR, 'butler_live.log'), 'ab')
    subprocess.Popen(['nohup', sys.executable, os.path.join(BASE_DIR, 'butler.py'), root],
                     stdout=lg, stderr=lg, stdin=subprocess.DEVNULL, start_new_session=True)
    say(f"🤵 butler running in background on: {os.path.basename(root)}  ·  peek: log  ·  end: stop")

def do_stop(say=print):
    import subprocess
    subprocess.run(['pkill', '-f', 'butler.py'], capture_output=True)
    say("🛑 butler stopped")

HELP_CARD = """
🤵 BUTLER CHAT - COMMAND CARD
 brief / all ................ full company board
 <any question> ............. "interviews tomorrow?", "feedback pending?", "call Isha"
 focus <positions> .......... set working positions (comma-separated)
 focus / focus clear ........ show / forget (+ stop watchers)
 missed <name> .............. missed-call WhatsApp draft
 missed  <number> <Name> .. missed-call template to a pasted number (Naukri tab - no CV needed)
 history <name>       .. stage transitions for one candidate
 stale [days]         .. candidates in current stage longer than N days (default 7)
 wa <name> <your words> .... free-text WhatsApp (phone auto-found)
 reject <name> .............. rejection draft, one person
 text <tag> ................. walk a tag folder, draft each
 update <name> .............. new CV takes the name, old -> Previous Versions
 where <name> / "take me to..."  locate + reveal in Finder
 open <folder word> ......... open client/position/tag folder in Finder
 phone <name> ............... just the number(s)
 recent [days] .............. everything touched lately (default 1 day)
 dedupe ..................... duplicates report (eyes-only)
 template ................... show message wording
 log [n] / start / stop ..... background butler control
 help / ? ................... this card
 quit ....................... exit + stop watchers
"""

def _hits_for(q, root):
    q = q.lower().strip()
    hits = []
    for dp, dn, fnames in os.walk(root):
        dn[:] = [d for d in dn if not d.startswith('.')]
        for f in fnames:
            if f.lower().endswith('.pdf') and all(t in f.lower() for t in q.split() if len(t) > 2):
                hits.append(os.path.join(dp, f))
    return hits

def _llm_prose(s):
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as r:
            names = [m['name'] for m in json.loads(r.read().decode()).get('models', []) if 'embed' not in m['name'].lower()]
        if not names: return None
        payload = json.dumps({"model": names[0], "messages": [{"role": "user", "content": f"Rewrite these recruiter facts as exactly two client-facing sentences, plain text, no preamble: {s}"}], "stream": False}).encode()
        req = urllib.request.Request("http://localhost:11434/api/chat", data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            t = (json.loads(r.read().decode())['message']['content'] or '').strip()
        return t if 20 < len(t) < 400 else None
    except Exception:
        return None
def do_summarize(arg, root, say=print):
    q = (arg or '').strip()
    if not q: say('usage: summarize <candidate name>'); return
    hits = _hits_for(q, root)
    if not hits: say(f"🤷 no CV matches '{q}'"); return
    hit = hits[0]
    import fitrank, ledger, time as _tm
    txt = fitrank._text(hit)
    yrs, des, loc = fitrank._years(txt), fitrank._desig(txt), fitrank._loc(txt)
    nt, ctc = fitrank._notice(txt), fitrank._ctc(txt)
    cs = ledger._load(ledger.CASES).get(os.path.splitext(os.path.basename(hit))[0].lower(), {})
    sts = cs.get('stages') or []
    stage = sts[0]['stage'] if sts else 'untracked'
    days = (int(_tm.time()) - sts[0]['at']) // 86400 if sts else 0
    conv = {}
    try: conv = json.load(open(os.path.join(BASE_DIR, 'conversations.json')))
    except Exception: conv = {}
    phs = cs.get('phones') or phones_of(hit) or ['']
    din = re.sub(r'\D', '', str(phs[0])) if phs else ''
    e = conv.get(din) if din else None
    li = next((m for m in reversed((e or {}).get('messages', [])) if m['dir'] == 'in'), None) if e else None
    liq = (li['text'][:70] if li else None)
    desig = ' / '.join(sorted(set(des))[:3]) or 'professional'
    facts = []
    if yrs: facts.append(f'{yrs}+ years')
    if loc: facts.append(', '.join(loc[:2]))
    if nt: facts.append(f'{nt}-day notice')
    if ctc: facts.append(f'~{ctc}L')
    line1 = f"{_full_name(hit)} - {desig} ({', '.join(facts) or 'experience on file'})"
    line2 = f"Currently {stage} ({days}d) · tier {cs.get('tier') or '?'} · last inbound: " + (f'"{liq}"' if liq else 'none captured')
    say('📝 client-ready:')
    say(f'   {line1}.')
    say(f'   {line2}.')
    p = _llm_prose(line1 + '. ' + line2)
    if p: say(f'   polished: {p}')

def do_tpltest(arg, root, say=print):
    hits = _hits_for((arg or '').strip(), root)
    if not hits: say(f'🤷 no CV matches {arg!r}'); return
    hit = hits[0]
    pos, cli = _pos_client_for(hit, None)
    title, loc = _split_pos(pos)
    at = cli + (f', {loc}' if loc else '')
    say(f'🧪 path: {os.path.relpath(hit, root)}')
    say(f'   position raw : {pos}')
    say(f'   client       : {cli}')
    say(f'   title        : {title}')
    say(f'   location     : {loc or "(none found)"}')
    say(f'   where        : {at}')
    say('   rendered (awaiting voice):')
    for ln in _fmt_tpl(_tpl_for(['awaiting']), hit, None, _full_name(hit)).split('\n'):
        say(f'     {ln}')

def do_help(say=print):
    say(HELP_CARD)

def do_open(arg, root, say=print):
    q = arg.lower().strip()
    if not q:
        say("usage: open <client | position | tag folder>"); return
    matches = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if not d.startswith('.')]
        for d in dn:
            if q in d.lower():
                matches.append(os.path.join(dp, d))
    if not matches:
        say(f"🤷 no folder matching '{arg}'"); return
    matches.sort(key=lambda x: (x.count(os.sep), len(x)))
    import subprocess
    subprocess.run(['open', matches[0]])
    say(f"📂 opened: {os.path.relpath(matches[0], root)}" + (f"   (+{len(matches)-1} more matched)" if len(matches) > 1 else ""))

def do_recent(arg, root, say=print):
    import time as _tm, datetime as _dt
    try: days = float(arg.strip() or 1)
    except ValueError: days = 1.0
    cut = _tm.time() - days * 86400
    hits = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if not d.startswith('.')]
        for f in fn:
            pth = os.path.join(dp, f)
            try:
                mt = os.path.getmtime(pth)
                if mt >= cut: hits.append((mt, os.path.relpath(pth, root)))
            except OSError:
                pass
    hits.sort(reverse=True)
    if not hits:
        say(f"🍃 nothing touched in the last {days:g} day(s)"); return
    say(f"🕒 {len(hits)} file(s) touched in the last {days:g} day(s):")
    for mt, rel in hits[:40]:
        say(f"   {_dt.datetime.fromtimestamp(mt).strftime('%d %b %H:%M')}  {rel}")

PHONE_FIX = os.path.join(BASE_DIR, "phone_fixes.json")
def _fix_load():
    try: return json.load(open(PHONE_FIX))
    except Exception: return {}

def do_phonefix(arg, root, say=print):
    if '=' not in arg:
        say("usage: phonefix <name or scan#> = <10-digit number>[, <another>]   (right side 'clear' removes)"); return
    q, rhs = [x.strip() for x in arg.split('=', 1)]
    digs = [d for d in re.findall(r'\d{10}', rhs.replace(' ', ''))] if rhs.strip() not in ('', 'clear') else []
    if rhs.strip() not in ('', 'clear') and not digs:
        say("🤷 no 10-digit number found on the right side"); return
    hit = None
    if q.strip().isdigit() and '_scan_path' in globals():
        hit = _scan_path(q.strip(), root)
        if not hit:
            say(f"🤷 no file at scan number {q.strip()}"); return
    if not hit:
        f = _read_focus(); base = (f or {}).get('path') or root
        ql = q.lower()
        for scan_root in (base, root):
            for dp, dn, fnames in os.walk(scan_root):
                for x in fnames:
                    if x.lower().endswith('.pdf') and all(t in x.lower() for t in ql.split() if len(t) > 2):
                        hit = os.path.join(dp, x); break
                if hit: break
            if hit: break
    if not hit:
        say(f"🤷 no candidate like '{q}'"); return
    key = re.sub(r'[^a-z]', '', os.path.splitext(os.path.basename(hit))[0].lower())
    store = _fix_load()
    if not digs:
        store.pop(key, None); say(f"🧹 phone override cleared for {os.path.basename(hit)}")
    else:
        store[key] = digs
        say(f"✅ phone fixed for {os.path.basename(hit)}: {', '.join(digs)} - every draft, table and command uses this now")
    json.dump(store, open(PHONE_FIX, 'w'), indent=2)

def do_phone(arg, root, say=print):
    if arg.strip().isdigit():
        pp = _scan_path(arg.strip(), root)
        if pp:
            say(f"📞 {os.path.basename(pp)}: {phone_of(pp) or 'no phone inside CV'}"); return
        say(f"🤷 no file at scan number {arg.strip()}"); return
    hits = _hits_for(arg, root)
    if not hits:
        say(f"🤷 no CV matches '{arg}'"); return
    for h in hits[:5]:
        say(f"📞 {os.path.basename(h)}: {phone_of(h) or 'no phone inside CV'}")

def do_wa(arg, root, say=print, ask=None):
    arg = (arg or '').strip()
    f = _read_focus()
    base = (f or {}).get('path') or root
    toks = arg.split()
    toks0 = toks
    if toks0 and re.fullmatch(r'[6-9]\d{9}', toks0[0]):
        msg = ' '.join(toks0[1:]).strip()
        if not msg:
            say("usage: wa <10-digit number> <your message>"); return
        askfn = locals().get('ask')
        try:
            import wa
            try: wa.send_review(toks0[0], msg, say, **({'ask': askfn} if askfn else {}))
            except TypeError: wa.send_review(toks0[0], msg, say)
        except Exception as e:
            say(f"⚠️ whatsapp failed: {e}")
        return
    hit = None; ntok = 0
    if toks and toks[0].isdigit():
        hit = _scan_path(toks[0], root); ntok = 1
        if not hit:
            say(f"🤷 no file at scan number {toks[0]} in the latest scan"); return
    for n in ([] if hit else (3, 2, 1)):
        if len(toks) <= n: continue
        q = ' '.join(toks[:n]).lower()
        for dp, dn, fnames in os.walk(base):
            dn[:] = [d for d in dn if not d.startswith('.')]
            for x in fnames:
                if x.lower().endswith('.pdf') and all(t in x.lower() for t in q.split() if len(t) > 2):
                    hit = os.path.join(dp, x); ntok = n; break
            if hit: break
        if hit: break
    if not hit:
        say(f"🤷 no candidate matching the start of: {arg}"); return
    msg = ' '.join(toks[ntok:]).strip()
    if not msg:
        say("usage: wa <name> <your message>"); return
    phone = _pick_phone(_phones_by_basename(hit) or phones_of(hit), say, path=hit)
    if not phone:
        say("🤷 no phone found in that CV"); return
    try:
        import wa
        wa.send_review(phone, msg, say, ask=ask)
    except Exception as e:
        say(f"⚠️whatsapp failed: {e}")

def _cli_root():
    f = _read_focus()
    if f: return f['path']
    try:
        r = open(os.path.expanduser('~/.cvtool_last_butler_root')).read().strip()
        if r and os.path.isdir(r): return r
    except Exception:
        pass
    raise SystemExit('no focus and no last butler root - open chat and: focus <position>')
def _cli(argv):
    cmd = argv[0].lower(); arg = " ".join(argv[1:])
    root = _cli_root()
    if cmd == 'missed': do_missed(arg, root, print)
    elif cmd == 'wa': do_wa(arg, root, print)
    elif cmd == 'jd': do_send(arg, root, ['jd shared'], print)
    elif cmd == 'nudge': do_missed(arg, root, print, words=['awaiting', 'confirmation'])
    elif cmd == 'history': do_history(arg, root, print)
    elif cmd == 'stale': do_stale(arg, root, print)
    elif cmd == 'fixphone': do_fixphone(arg, root, print)
    elif cmd == 'call': import fitrank; fitrank.show(root, arg, 'call', print)
    elif cmd == 'next': import fitrank; fitrank.show(root, arg, 'next', print)
    elif cmd == 'case': import ledger; ledger.show_case(arg, print)
    elif cmd == 'positions': import ledger; ledger.show_positions(arg, print)
    elif cmd == 'note': import ledger; ledger.note(arg, print)
    elif cmd == 'interview': import ledger; ledger.interview(arg, print)
    elif cmd == 'offer': import ledger; ledger.offer(arg, print)
    elif cmd == 'due': import cadence; cadence.show_due(print)
    elif cmd == 'outbox': import cadence; cadence.run_outbox(root, print)
    elif cmd == 'ack': import cadence; cadence.ack(arg, print)
    elif cmd == 'money': import ledger; ledger.show_money(arg, print)
    elif cmd == 'value': import ledger; ledger.show_value(arg, print)
    elif cmd == 'push': import ledger; ledger.show_push(arg, print)
    elif cmd == 'recap': import waread; waread.recap(print, show=('show' in arg))
    elif cmd == 'similar': import sem; sem.similar(arg, root, print)
    elif cmd == 'ghost': import sem; sem.ghost(arg, root, print)
    elif cmd == 'client': import sem; sem.client(arg, print)
    elif cmd == 'digest': import ledger; ledger.show_digest(arg, print)
    elif cmd == 'summarize': do_summarize(arg, root, print)
    elif cmd == 'clientname': do_clientname(arg, root, print)
    elif cmd == 'follow': do_missed(arg, root, print, words='AUTO')
    elif cmd == 'tpltest': do_tpltest(arg, root, print)
    elif cmd == 'refer': do_send(arg, root, ['referral'], print)
    elif cmd == 'renwhy': do_renwhy(arg, root, print)
    elif cmd == 'name': do_name(arg, root, print)
    elif cmd == 'adlog': do_adlog(arg, root, print)
    elif cmd == 'due': import cadence; cadence.show_due(print)
    elif cmd == 'outbox': import cadence; cadence.show_outbox(print)
    elif cmd == 'ack': import cadence; cadence.ack(arg, print)
    elif cmd == 'touch': do_send(arg, root, ['touch'], print)
    elif cmd in ('brief', 'board'): print_briefing(root)
    else: print('cli: missed | wa | jd | nudge | touch | brief  <args>')

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() in ('missed','wa','jd','nudge','touch','brief','board','history','stale','fixphone','call','next','case','positions','note','interview','offer','due','outbox','ack','money','value','push','recap','similar','ghost','client','digest','summarize','clientname','follow','tpltest','refer','renwhy','name','adlog'):
        _cli(sys.argv[1:]); raise SystemExit(0)
    LAST = os.path.expanduser("~/.cvtool_last_root")
    args = sys.argv[1:]
    mode = 'brief'
    root = None
    for a in args:
        if a.lower() == 'chat':
            mode = 'chat'
        else:
            root = a
    if not root:
        try:
            root = open(LAST).read().strip()
        except Exception:
            root = None
    if not root or not os.path.isdir(root):
        print("first time give a folder:  brief \"<folder>\" / chat \"<folder>\" - after that plain brief/chat remembers it")
        sys.exit(1)
    with open(LAST, 'w') as f:
        f.write(root)
    if mode == 'chat':
        print(f"🤖 butler chat - 📂 {root}")
        print("   ask anything ('interviews tomorrow?', 'feedback pending?', 'call Isha') - type quit")
        live = []
        for fn in os.listdir(BASE_DIR):
            if fn.startswith('butler_') and fn.endswith('.lock'):
                try:
                    parts = open(os.path.join(BASE_DIR, fn)).read().strip().split('|')
                    pid = int(parts[0]); os.kill(pid, 0)
                    if len(parts) > 1 and os.path.isdir(parts[1]): live.append(parts[1])
                except Exception:
                    pass
        live = [r for r in live if os.path.abspath(r) == os.path.abspath(root)
                or os.path.abspath(r).startswith(os.path.abspath(root) + os.sep)
                or os.path.abspath(root).startswith(os.path.abspath(r) + os.sep)]
        if live:
            pickr = live[0]
            if len(live) > 1:
                print("   🤖 butlers running:")
                for i, r in enumerate(live): print(f"      {i+1}) {os.path.relpath(r, root)}")
                try: pickr = live[int(input("   sync focus to #: ").strip()) - 1]
                except Exception: pass
            json.dump({'path': pickr, 'display': clean_pos(os.path.basename(pickr)),
                       'client': re.sub(r'^\d+[\s_-]*', '', os.path.basename(os.path.dirname(pickr))), 'also': []},
                      open(FOCUS_FILE, 'w'), indent=2)
            print(f"   🎯 focus synced to running butler: {os.path.relpath(pickr, root)}")
        while True:
            try:
                q = input("you> ").strip()
                if butler.listen_teach(q): continue  # LISTEN v81.67: after a no-phone confession, the master's bare ten digits are the lesson
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\n👋 chat closed - watchers keep running (focus clear stops them)")
                break
            if not q or q.lower() in ('quit', 'exit', 'q'):
                try:
                    alive = 0
                    for t in open(WATCH_PID).read().split():
                        try:
                            os.kill(int(t), 0); alive += 1
                        except Exception: pass
                    if alive: say(f"   🤖 {alive} watcher(s) keep running in background - 'focus clear' stops them")
                except Exception: pass
                break
            if q.startswith('desk'): do_desk(q[4:].strip(), root); continue  # DESK v84.0
            if q.startswith('briefing'): do_briefing(q[8:].strip(), root); continue
            if q.startswith('chase'): do_chase(q[5:].strip(), root); continue
            if q.startswith('tag '): do_tagcmd(q[4:].strip(), root); continue  # TAG-VOICE v84.0
            if q.strip().lower() in ('y', 'yes', 'ok', 'confirm') and butler.action_pending(): do_confirm(q, root); continue  # PROPOSE-ROUTE v84.4
            if q.strip().lower() in ('n', 'no', 'cancel') and butler.action_pending(): do_cancel(q, root); continue
            if q.strip().isdigit() and butler.tag_pick_pending(): do_tagcmd(q.strip(), root); continue  # TAG-PICK-ROUTE v84.3: a bare digit answers the fresh question before the AI wakes
            if q.startswith('dash'): do_dash(q[4:].strip(), root); continue  # DASH v84.7
            if q.startswith('audit'): do_audit(q[5:].strip(), root); continue
            if q.startswith('tidy'): do_tidy(q[4:].strip(), root); continue  # TIDY v84.9
            if q.strip() in ('?', 'help', 'menu'):  # MENU v84.10a
                say('🤵 The 4-Word Life:')
                say('  📆 briefing     · what is due today')
                say('  🏷️ tag <n> <s>  · update a human (e.g. tag lalan feedback pending)')
                say('  🧹 tidy         · carry misplaced papers home')
                say('  👀 dash         · see the desk\'s census')
                continue
            if butler.sheet_current() and q.strip() in ('jd', 'missed', 'nudge', 'refer'): q = q + ' ' + os.path.splitext(os.path.basename(butler.sheet_current()['p']))[0]  # CHAIR-KEYWORD v84.30
            if q.startswith('draftwhy '): do_draftwhy(q[9:].strip(), root, print); continue  # DRAFT-WHY v84.33
            if q == 'twins' or q.startswith('twins '): butler.twins_cmd(q[5:].strip(), root, print); continue  # TWINS v84.36
            if q.startswith('skipfolder '): butler.skipfolder_cmd(q[11:].strip(), root, print); continue  # NON-QUEUE v84.39
            if q.strip() == 'weekly': butler.weekly_cmd('', root, print); continue  # WEEKLY v84.40
            if q.strip() == 'refresh': butler.calls_cmd('', root, print); continue  # SELF-REFRESH v84.32
            if q.strip() == 'options': butler.options_cmd('', root, print); continue  # OPTIONS-MAP v84.32
            if butler.sheet_current() and q.strip() in ('1', '2', '3', '4', '5', '6', '7'): do_outcome(q.strip(), root); continue  # CHAIR v84.10b
            if butler.sheet_current() and butler.chair_word(q): do_outcome(butler.chair_word(q), root); continue
            if q == 'up' or q.startswith('up '): do_up(q[2:].strip(), root); continue
            if q.startswith('calls'): do_calls(q[5:].strip(), root); continue
            if q.startswith('sheet'): do_sheet(q[5:].strip(), root); continue
            if q.startswith('unskip '): butler.unskip_cmd(q[7:].strip(), root, print); continue  # SKIP v84.11
            if q.startswith('forget '): butler.forget_cmd(q[7:].strip(), root, print); continue  # COVERED-MEMORY v84.15
            if q.startswith('meta '): butler.meta_cmd(q[5:].strip(), root, print); continue  # TEMPLATES v84.16
            if q.startswith('client '): butler.client_cmd(q[7:].strip(), root); continue  # POS-ID v84.21  # CLIENT-DISPATCH v84.25
            if q.strip() == 'clients': butler.clients_cmd('', root); continue  # CLIENTS-LIST v84.24
            if q.startswith('posmeta '): butler.posmeta_cmd(q[8:].strip(), root); continue
            if q.startswith('followup'): butler.followup_cmd(q[8:].strip(), root, print); continue  # FOLLOWUP v84.11
            if q.startswith('pending'): do_pending(q[len('pending'):].strip(), root); continue  # PIPELINE-CHAT-SHALLOW v83.1: the master's words stand at the head of the chain, never nested under another voice
            if q.startswith('status'): do_status(q[len('status'):].strip(), root); continue
            if q.startswith('note'): do_note(q[len('note'):].strip(), root); continue
            if q.lower().startswith('focus'):
                do_focus(q[5:], root); continue
            if q.lower().startswith('missed'):
                do_missed(q[6:], root); continue
            if q.lower().startswith('history '): do_history(q[8:], root); continue
            if q.lower().startswith('history'): do_history(q[7:].strip(), root); continue
            if q.lower().startswith('stale'): do_stale(q[5:].strip(), root); continue
            if q.lower().startswith('fixphone '): do_fixphone(q[9:], root); continue
            if q.lower().startswith('call '): import fitrank; fitrank.show(root, q[5:].strip(), 'call'); continue
            if q.lower().startswith('next'): import fitrank; fitrank.show(root, q[4:].strip(), 'next'); continue
            if q.lower().startswith('case '): import ledger; ledger.show_case(q[5:].strip()); continue
            if q.lower().startswith('positions'): import ledger; ledger.show_positions(q[9:].strip()); continue
            if q.lower().startswith('due'): import cadence; cadence.show_due(); continue
            if q.lower().startswith('outbox'): import cadence; cadence.run_outbox(root); continue
            if q.lower().startswith('ack '): import cadence; cadence.ack(q[4:].strip()); continue
            if q.lower().startswith('money'): import ledger; ledger.show_money(q[5:].strip()); continue
            if q.lower().startswith('value'): import ledger; ledger.show_value(q[5:].strip()); continue
            if q.lower().startswith('push'): import ledger; ledger.show_push(q[4:].strip()); continue
            if q.lower().startswith('recap'): import waread; waread.recap(show=('show' in q)); continue
            if q.lower().startswith('similar '): import sem; sem.similar(q[8:].strip(), root); continue
            if q.lower().startswith('ghost'): import sem; sem.ghost(q[5:].strip(), root); continue
            if q.lower().startswith('client '): import sem; sem.client(q[7:].strip()); continue
            if q.lower().startswith('digest'): import ledger; ledger.show_digest(q[6:].strip()); continue
            if q.lower().startswith('summarize '): do_summarize(q[10:].strip(), root); continue
            if q.lower().startswith('clientname '): do_clientname(q[11:].strip(), root); continue
            if q.lower().startswith('follow '): do_missed(q[7:].strip(), root, words='AUTO'); continue
            if q.lower().startswith('tpltest '): do_tpltest(q[8:].strip(), root); continue
            if q.lower().startswith('refer '): do_send(q[6:].strip(), root, ['referral']); continue
            if q.lower().startswith('renwhy '): do_renwhy(q[7:].strip(), root); continue
            if q.lower().startswith('name '): print('📖 chat is read-only - run: briefing.py name <phone-or-word> <Name>'); continue  # CHAT-READONLY v80
            if q.lower().startswith('adlog'): do_adlog(q[5:].strip(), root); continue
            if q.lower().startswith('due'): import cadence; cadence.show_due(); continue
            if q.lower().startswith('outbox'): import cadence; cadence.show_outbox(); continue
            if q.lower().startswith('ack '): import cadence; cadence.ack(q[4:].strip()); continue
            if q.lower().startswith('text '):
                do_text(q[5:], root); continue
            if q.lower().startswith('reject'):
                do_reject(q[6:], root); continue
            if q.lower().startswith('jd '):
                do_send(q[3:], root, ['jd shared']); continue
            if q.lower().startswith('nudge '):
                do_send(q[6:], root, ['awaiting', 'confirmation']); continue
            if q.lower().startswith('touch '):
                do_send(q[6:], root, ['keep', 'touch']); continue
            if q.lower().startswith('name '):
                if q.lower().startswith('name '): print('📖 chat is read-only - run: briefing.py name <phone-or-word> <Name>'); continue  # CHAT-READONLY v80
            if q.lower() == 'template':
                print("📝 " + _read_tpl())
                print(f"   (to change it, edit: {TPL_FILE})")
                continue
            if q.lower() == 'company':
                print_briefing(_company_root(root)); continue
            if q.lower() in ('all', 'brief', 'briefing'):
                print_briefing(root); continue
            if q.lower() in ('help', '?'):
                do_help(); continue
            if q.lower().startswith('wa '):
                do_wa(q[3:], root); continue
            if q.lower().startswith('update '):
                do_update(q[7:], root); continue
            if q.lower().startswith('where '):
                do_where(q[6:], root); continue
            if q.lower().startswith(('phonefix ', 'fixphone ')):
                do_phonefix(q.split(' ', 1)[1], root); continue
            if q.lower().startswith('phone '):
                do_phone(q[6:], root); continue
            if q.lower().startswith('recent'):
                do_recent(q[6:], root); continue
            if q.lower().startswith('open '):
                do_open(q[5:], root); continue
            if q.lower().startswith('log'):
                do_log(int(q[3:].strip() or 25)); continue
            if q.lower().startswith('start'):
                do_start(q[5:].strip()); continue
            if q.lower() == 'stop':
                do_stop(); continue
            answer(root, q)
    else:
        print_briefing(root)

def do_list(root, say=print):
    rows = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [x for x in dn if not x.startswith('.')]
        for f in fn:
            if not f.startswith('.'): rows.append(os.path.join(dp, f))
    idx, ino = {}, {}
    say('📇 live phone book - ' + os.path.basename(root))
    shown = 0
    for n, fp in enumerate(rows, 1):
        idx[str(n)] = os.path.abspath(fp)
        try: ino[str(n)] = os.stat(fp).st_ino
        except OSError: pass
        if not fp.lower().endswith('.pdf'): continue
        ph = phones_of(fp) if 'phones_of' in globals() else [phone_of(fp)]
        ph = (ph or [''])[0] if isinstance(ph, list) else ph
        say('   %d) %s · %s · %s' % (n, os.path.splitext(os.path.basename(fp))[0], ph or 'no phone', os.path.relpath(fp, root)))
        shown += 1
    try:
        json.dump({'root': os.path.abspath(root), 'idx': idx, 'ino': ino},
                  open(_idx_path(root), 'w'))
    except Exception: pass
    say('   %d CV(s) - numbers are live right now: jd/missed/wa/nudge <number>' % shown)
