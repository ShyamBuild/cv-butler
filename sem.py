import os, re, json, time, math, hashlib
BASE = os.path.dirname(os.path.abspath(__file__))
IDX = os.path.join(BASE, 'sem_index.json'); DIM = 512
def _load():
    try: return json.load(open(IDX))
    except Exception: return {}
def _save(d):
    t = IDX + '.tmp'; json.dump(d, open(t, 'w'), indent=2); os.replace(t, IDX)
def _ollama_embed(text):
    try:
        import urllib.request
        with urllib.request.urlopen('http://localhost:11434/api/tags', timeout=3) as r:
            names = [m['name'] for m in json.loads(r.read().decode()).get('models', []) if 'embed' in m['name'].lower()]
        if not names: return None
        payload = json.dumps({'model': names[0], 'prompt': text[:4000]}).encode()
        req = urllib.request.Request('http://localhost:11434/api/embeddings', data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode()).get('embedding') or None
    except Exception:
        return None
def _hash_vec(text):
    import fitrank
    v = [0.0] * DIM
    for t in fitrank._kw(text, 80):
        v[int(hashlib.md5(t.encode()).hexdigest(), 16) % DIM] += 1.0
    return v
def _norm(v):
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]
def _cos(a, b):
    if len(a) != len(b):
        b = (b + [0.0] * len(a))[:len(a)] if len(b) < len(a) else b[:len(a)]
    return sum(x * y for x, y in zip(a, b))
def tick(B, budget=2):
    import fitrank
    d = _load()
    for pos in fitrank.positions(B.root):
        for f in os.listdir(pos):
            if budget <= 0: break
            lf = f.lower()
            if not lf.endswith('.pdf') or lf.startswith('jd') or ' jd' in lf: continue
            stem = os.path.splitext(f)[0]; fp = os.path.join(pos, f)
            try: st = os.stat(fp)
            except OSError: continue
            key = f'{st.st_mtime_ns}|{st.st_size}'
            e = d.get(stem)
            if e and e.get('key') == key: continue
            txt = fitrank._text(fp)
            if not txt.strip(): continue
            v = _ollama_embed(txt[:6000]); mdl = 'ollama'
            if not v: v = _hash_vec(txt); mdl = 'hash'
            d[stem] = {'vec': _norm(v), 'key': key, 'at': int(time.time()), 'pos': os.path.basename(pos), 'model': mdl}
            budget -= 1
        if budget <= 0: break
    _save(d)
def similar(arg, root=None, say=print, top=5):
    import ledger
    d = _load()
    if not d: say('semantic index empty - it fills a couple of CVs per sweep'); return
    q = (arg or '').strip()
    stem = next((k for k in d if k.lower() == q.lower() or q.lower() in k.lower()), None)
    qv = d[stem]['vec'] if stem else None
    if qv is None:
        v = _ollama_embed(q)
        qv = _norm(v if v else _hash_vec(q))
    rows = [(_cos(qv, e['vec']), k, e) for k, e in d.items() if k != stem]
    say(f'🔗 most similar to {stem or q!r}:')
    cs = ledger._load(ledger.CASES)
    for s, k, e in sorted(rows, reverse=True)[:top]:
        c = cs.get(k.lower(), {})
        say(f"   {s:.2f} · {k} · {e.get('pos', '')} · tier {c.get('tier') or '?'} · {(c.get('phones') or ['?'])[0]}")
def ghost(arg=None, root=None, say=print):
    import ledger
    cs = ledger._load(ledger.CASES)
    try: conv = json.load(open(os.path.join(BASE, 'conversations.json')))
    except Exception: conv = {}
    now = int(time.time()); out = []
    ACTIVE = ('call scheduled', 'feedback pending', 'awaiting jd confirmation', 'awaiting cv update', 'interview scheduled')
    for k, c in cs.items():
        sts = c.get('stages') or []
        st = (sts[0].get('stage') or '').lower() if sts else ''
        if not any(a in st for a in ACTIVE): continue
        lc = c.get('last_contact') or 0
        if not lc: continue
        days = (now - lc) // 86400
        if days < 5: continue
        inbound = any((conv.get(re.sub(r'\D', '', str(p))) or {}).get('messages', [{}])[-1].get('dir') == 'in' for p in (c.get('phones') or []))
        out.append((days, c.get('name') or k, st, 'reply seen' if inbound else 'silent'))
    if not out: say('👻 no ghost risks right now'); return
    say('👻 ghost risks (active stage, silent >=5d):')
    for days, nm, st, note in sorted(out, reverse=True)[:10]:
        say(f'   {days:3d}d · {nm} · {st} · {note} -> nudge or close')
def client(arg, say=print):
    import ledger
    pos = ledger._load(ledger.POS); cs = ledger._load(ledger.CASES)
    w = (arg or '').strip().lower()
    rows = [(pp, e) for pp, e in pos.items() if not w or w in (e.get('client') or '').lower()]
    if not rows: say(f'no client matching {arg!r}'); return
    for cn in sorted({e['client'] for pp, e in rows}):
        cpos = [pp for pp, e in rows if e['client'] == cn]
        placed = total = days_sum = days_n = 0
        for k, c in cs.items():
            if not any(pp in (c.get('positions') or []) for pp in cpos): continue
            total += 1
            sts = c.get('stages') or []
            if any('joined' in (s.get('stage') or '').lower() or 'payment' in (s.get('stage') or '').lower() for s in sts):
                placed += 1
                if len(sts) >= 2: days_sum += (sts[0]['at'] - sts[-1]['at']) // 86400; days_n += 1
        open_n = sum(1 for pp, e in rows if e['client'] == cn and e.get('status') == 'open')
        say(f'🏢 {cn}: {total} candidate(s), {placed} placement(s), {(placed / total * 100) if total else 0:.0f}% conversion, avg {(days_sum // days_n) if days_n else 0}d first-stage→join, {open_n} open position(s)')
