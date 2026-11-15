import ast
def ind(l): return len(l) - len(l.lstrip())
p = 'briefing.py'; L = open(p).read().split('\n'); done = []

BOARD = [('("awaiting jd confirmation",', '("awaiting jd confirmation", "📤 JD SHARED - ACK PENDING", "acknowledgement awaited"),'),
         ('("interview cleared",',        '("interview cleared",        "🎉 INTERVIEW CLEARED", "next round / offer"),'),
         ('("expected to join",',         '("expected to join",         "🚪 EXPECTED TO JOIN", "onboarding follow-up"),'),
         ('("joined - payment pending",', '("joined - payment pending", "💰 JOINED - PAYMENT PENDING", "invoice follow-up"),'),
         ('("payment received",',         '("payment received",         "✅ PAYMENT RECEIVED", ""),'),
         ('("closed - not proceeding",',  '("closed - not proceeding",  "🚫 CLOSED - NOT PROCEEDING", "tag removed = off the board"),'),
         ('("rejected by client",',       '("rejected by client",       "❌ REJECTED BY CLIENT", ""),'),
         ('("position active",',          '("position active",          "🟢 POSITION ACTIVE", ""),'),
         ('("position on hold",',         '("position on hold",         "🟡 POSITION ON HOLD", ""),'),
         ('("position closed",',          '("position closed",          "⚫ POSITION CLOSED", ""),')]
missing = [t for probe, t in BOARD if not any(l.strip().startswith(probe) for l in L)]
if missing:
    anchor = next((i for i, l in enumerate(L) if 'awaiting cv update' in l and 'CV UPDATE' in l), None)
    if anchor is not None:
        d = ind(L[anchor])
        L[anchor+1:anchor+1] = [d*' ' + t for t in missing]
        done.append('board+%d' % len(missing))

if 'def _tags_of(' not in '\n'.join(L):
    i = next(k for k, l in enumerate(L) if l.startswith('def collect(root):'))
    j = next((k for k in range(i, len(L)) if L[k].startswith('def render(')), len(L))
    new = '''COLOR_TAGS = {'Red','Orange','Yellow','Green','Blue','Purple','Gray','Grey'}
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
            nm = str(t).split('\\n')[0].strip()
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
                nm = line.split('\\n')[0].strip()
                if nm and nm not in COLOR_TAGS: tags.append(nm)
            return tags
        except Exception:
            return []
def _pos_for(fp, root):
    d = os.path.dirname(fp)
    tagset = {k for k, _, _ in TAGS} | FOCUS_SKIP
    while d and os.path.abspath(d) != os.path.abspath(root):
        bn = os.path.basename(d).lower().replace('\\u2013', '-')
        if bn not in tagset:
            return clean_pos(os.path.basename(d))
        d = os.path.dirname(d)
    return clean_pos(os.path.basename(root))
def collect(root):
    data = {k: [] for k, _, _ in TAGS}
    cache = _load_tags_cache(); dirty = False
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if not d.startswith('.') and d.lower() not in SKIP_DIRS]
        for f in fn:
            if not f.lower().endswith('.pdf') or f.startswith('.'): continue
            fp = os.path.join(dp, f)
            try: mt = os.path.getmtime(fp)
            except OSError: continue
            crc = _xattr_crc(fp)
            key = os.path.abspath(fp)
            e = cache.get(key)
            if e and e[0] == mt and e[1] == crc:
                tags = e[2]
            else:
                tags = _tags_of(fp)
                cache[key] = [mt, crc, tags]; dirty = True
            low = {t.lower().replace('\\u2013', '-') for t in tags}
            if not low: continue
            pos = _pos_for(fp, root)
            ph = ''
            try:
                ps = phones_of(fp) if 'phones_of' in globals() else [phone_of(fp)]
                ph = (ps or [''])[0] if isinstance(ps, list) else ps
            except Exception:
                ph = phone_of(fp)
            for k in data:
                if k in low:
                    data[k].append([os.path.splitext(f)[0], pos, ph])
    if dirty: _save_tags_cache(cache)
    return data
'''
    L[i:j] = new.split('\n')
    done.append('tag-driven-collect')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('briefing:', done or 'nothing missing')
