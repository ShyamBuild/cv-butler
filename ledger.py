import os, re, json, time
BASE = os.path.dirname(os.path.abspath(__file__))
CASES = os.path.join(BASE, 'cases.json'); POS = os.path.join(BASE, 'positions.json')
def _n(s): return (s or '').strip().lower()
def _load(p):
    try: return json.load(open(p)) if os.path.exists(p) else {}
    except Exception: return {}
def _save(p, d):
    try:
        t = p + '.tmp'; json.dump(d, open(t, 'w'), indent=2); os.replace(t, p)
    except Exception: pass
def _case(d, name):
    k = _n(name)
    if k not in d: d[k] = {'name': name.strip().title(), 'phones': [], 'stages': [], 'notes': [], 'interviews': [], 'offer': None, 'joining': None, 'references': {}, 'last_contact': 0, 'tier': None, 'positions': []}
    return d[k]
def tick(B):
    pos_d, case_d = _load(POS), _load(CASES)
    root = B.root
    try:
        from butler import StageLog; slog = StageLog(root)
    except Exception: slog = None
    fr = os.path.join(BASE, 'fit_rank'); tiers = {}
    if os.path.isdir(fr):
        for fn in os.listdir(fr):
            try:
                dd = json.load(open(os.path.join(fr, fn)))
                for f, r in dd.get('rows', {}).items(): tiers[_n(os.path.splitext(f)[0])] = (r.get('tier'), r.get('score'), r.get('sub'))
            except Exception: pass
    for c in sorted(os.listdir(root)):
        cp = os.path.join(root, c)
        if not os.path.isdir(cp) or c.startswith('.'): continue
        for pname in sorted(os.listdir(cp)):
            pp = os.path.join(cp, pname)
            if not os.path.isdir(pp) or pname.startswith('.'): continue
            pl = pname.lower()
            if pl.startswith(('jd', 'fw')) or pl.startswith('untitled') or pl in ('converted doc files', 'converted files', 'duplicates', 'previous versions', 'nvites', 'ta_output'): continue
            e = pos_d.setdefault(pp, {'client': c, 'title': pname, 'opened': int(time.time()), 'jd': None, 'status': 'open', 'pipeline': {}, 'selections': [], 'last_activity': 0})
            pipe = {}; latest = 0
            for sub in sorted(os.listdir(pp)):
                sp = os.path.join(pp, sub)
                if os.path.isdir(sp) and not sub.startswith('.'):
                    cnt = len([f for f in os.listdir(sp) if f.lower().endswith('.pdf')])
                    if cnt: pipe[sub] = cnt
                    for f in os.listdir(sp):
                        try: latest = max(latest, int(os.stat(os.path.join(sp, f)).st_mtime))
                        except Exception: pass
                elif os.path.isfile(sp):
                    try: latest = max(latest, int(os.stat(sp).st_mtime))
                    except Exception: pass
            e['pipeline'] = pipe; e['last_activity'] = latest
            e['idle_days'] = (int(time.time()) - (latest or e['opened'])) // 86400
            e['revisitable'] = e['status'] == 'open' and e['idle_days'] >= 14 and sum(pipe.values()) > 0
            for f in os.listdir(pp):
                if f.lower().endswith('.pdf'):
                    nm = os.path.splitext(f)[0]; cd = _case(case_d, nm)
                    if pp not in cd['positions']: cd['positions'].append(pp)
                    t = tiers.get(_n(nm))
                    if t: cd['tier'], cd['score'], cd['sub'] = t
                    if slog:
                        rows = slog.all_for(nm)
                        if rows:
                            cd['stages'] = [{'stage': r['stage'], 'at': r['ts'], 'position': r.get('position')} for r in reversed(rows)]
                            cd['last_contact'] = max(cd['last_contact'], rows[0]['ts'])
    try:
        pj = _load(os.path.join(BASE, 'phones.json'))
        byb = {}
        for k, v in pj.items():
            ph = v.get('phones') or []
            if not ph: continue
            byb.setdefault(os.path.basename(k).lower(), []).append((os.path.exists(k), ph))
        for nm, opts in byb.items():
            cd = _case(case_d, os.path.splitext(nm)[0])
            cd['phones'] = next((ph for ex, ph in opts if ex), None) or opts[0][1]
        for kk, vv in _load(os.path.join(BASE, 'phone_fixes.json')).items():
            tg = next((k2 for k2 in case_d if re.sub(r'[^a-z]', '', k2) == kk), None)
            if tg and isinstance(vv, list) and vv: case_d[tg]['phones'] = vv
    except Exception: pass
    _save(POS, pos_d); _save(CASES, case_d)
def show_case(arg, say=print):
    d = _load(CASES); k = _n(arg)
    hit = d.get(k) or next((v for kk, v in d.items() if k and (kk.startswith(k) or k in kk)), None)
    if not hit: say(f'no case for {arg!r} yet'); return
    say(f"📇 {hit['name']}  ·  {'+'.join(hit['phones']) or 'no phone'}  ·  tier {hit.get('tier') or '?'}")
    for s in hit['stages'][:6]:
        say(f"   {time.strftime('%Y-%m-%d', time.localtime(s['at']))}  {s['stage']}  ({os.path.basename(s.get('position') or '')})")
    for iv in hit['interviews']: say(f"   🗓 interview: {iv}")
    if hit.get('offer'): say(f"   💰 offer: {hit['offer']['ctc']}")
    for nte in hit['notes'][-3:]: say(f"   📝 {nte}")
    if hit.get('references'): say(f"   🔁 references: {hit['references']}")
def show_positions(arg, say=print):
    d = _load(POS)
    say('🗂 open positions (stalest first):')
    for pp, e in sorted(d.items(), key=lambda kv: -kv[1].get('idle_days', 0)):
        if e.get('status') != 'open': continue
        say(f"   {e.get('idle_days', 0):3d}d idle · {sum(e.get('pipeline', {}).values()):3d} CVs · {e['client']} / {e['title']}" + (' ⭐ revisitable' if e.get('revisitable') else ''))
def note(arg, say=print):
    parts = (arg or '').split(None, 1)
    if len(parts) < 2: say('usage: note <name> <text>'); return
    d = _load(CASES); cd = _case(d, parts[0]); cd['notes'].append(f"{time.strftime('%Y-%m-%d')}: {parts[1]}")
    _save(CASES, d); say('📝 noted')
def interview(arg, say=print):
    parts = (arg or '').split(None, 1)
    if len(parts) < 2: say('usage: interview <name> <when>'); return
    d = _load(CASES); cd = _case(d, parts[0]); cd['interviews'].append(parts[1])
    _save(CASES, d); say(f"🗓 interview logged: {parts[1]}")
def offer(arg, say=print):
    parts = (arg or '').split(None, 1)
    if len(parts) < 2: say('usage: offer <name> <ctc in lakhs>'); return
    d = _load(CASES); cd = _case(d, parts[0]); cd['offer'] = {'ctc': parts[1].strip(), 'at': int(time.time())}
    _save(CASES, d); say(f"💰 offer logged: {parts[1]} (incentive math lands in v43)")
