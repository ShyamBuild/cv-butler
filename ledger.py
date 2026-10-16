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
    # LEDGER-PRUNE v43.1
    for _kk in list(pos_d):
        _bl = os.path.basename(_kk).lower()
        if not os.path.isdir(_kk) or _bl.startswith(('jd', 'fw')) or _bl.startswith('untitled') or _bl in ('converted doc files', 'converted files', 'duplicates', 'previous versions', 'nvites', 'ta_output'):
            del pos_d[_kk]
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
    _save(CASES, d)
    # BOOKENDS v46
    ts = _parse_when(parts[1])
    if ts:
        import cadence, datetime as _dt
        lt = time.localtime(ts)
        day0 = _dt.datetime(lt.tm_year, lt.tm_mon, lt.tm_mday)
        cadence.queue(cd['name'], 'interview_eve', note=parts[1], due=int((day0 - _dt.timedelta(hours=5, minutes=30)).timestamp()))
        cadence.queue(cd['name'], 'interview_morning', note=parts[1], due=int((day0 + _dt.timedelta(hours=8, minutes=30)).timestamp()))
        cadence.queue(cd['name'], 'interview_feedback_ask', note=parts[1], due=int((day0 + _dt.timedelta(hours=19)).timestamp()))
        cadence.queue(cd['name'], 'interview_nextday_chase', note=parts[1], due=int((day0 + _dt.timedelta(days=1, hours=11)).timestamp()))
        say(f"🗓 interview logged: {parts[1]} · bookends armed (eve, 08:30, 19:00 feedback, next-day chase)")
    else:
        say(f"🗓 interview logged: {parts[1]} (date not parseable - bookends skipped; try e.g. 22 Oct 2pm)")
def offer(arg, say=print):
    parts = (arg or '').split(None, 1)
    if len(parts) < 2: say('usage: offer <name> <ctc in lakhs>'); return
    d = _load(CASES); cd = _case(d, parts[0]); cd['offer'] = {'ctc': parts[1].strip(), 'at': int(time.time())}
    _save(CASES, d); say(f"💰 offer logged: {parts[1]} (incentive math lands in v43)")

INC_RATE = 0.5 * 0.0833
def incentive_rupees(ctc_lakhs):
    try: return float(ctc_lakhs) * 100000.0 * INC_RATE
    except Exception: return 0.0
def _conv_rates():
    tot, win = {}, {}
    for k, c in _load(CASES).items():
        sts = [s['stage'].lower() for s in c.get('stages', [])]
        joined = any('join' in s or 'payment' in s for s in sts)
        for s in set(sts):
            tot[s] = tot.get(s, 0) + 1
            if joined: win[s] = win.get(s, 0) + 1
    return {s: (win.get(s, 0) / t) for s, t in tot.items() if t}
DEF_P = {'call scheduled': 0.25, 'interview scheduled': 0.4, 'interview cleared': 0.6, 'expected to join': 0.8, 'joined - payment pending': 0.95, 'payment received': 1.0, 'feedback pending': 0.2, 'ready for manager review': 0.3, 'awaiting cv update': 0.15, 'awaiting jd confirmation': 0.1}
def _p_join(stage):
    r = _conv_rates(); s = (stage or '').lower()
    if r.get(s): return r[s]
    for k, v in DEF_P.items():
        if k in s: return v
    return 0.1
def _ctc_for(pos_path):
    try:
        import fitrank
        sp = fitrank._store(pos_path)
        if os.path.exists(sp):
            c = fitrank._ctc(json.load(open(sp)).get('jdtext') or '')
            if c: return c
    except Exception: pass
    return None
def show_money(arg, say=print):
    d = _load(CASES)
    realized, pipe, n_sel = 0.0, 0.0, 0
    for k, c in d.items():
        o = c.get('offer'); ctc = 0.0
        if o:
            try: ctc = float(re.sub(r'[^\d.]', '', str(o.get('ctc', '')) or '0') or 0)
            except Exception: ctc = 0.0
        sts = [s['stage'].lower() for s in c.get('stages', [])]
        sel = c.get('joining') or any('join' in s or 'payment' in s for s in sts)
        if o and ctc and sel:
            realized += incentive_rupees(ctc); n_sel += 1
        elif sts:
            est = ctc or (_ctc_for(c['positions'][-1]) if c.get('positions') else None)
            if est: pipe += _p_join(sts[-1]) * incentive_rupees(est)
    say(f'💰 realized (selections with offers): ₹{realized:,.0f} across {n_sel} selection(s)')
    pos_pipe = 0.0
    for _pp, _e in _load(POS).items():
        if _e.get('status') != 'open': continue
        _c = _ctc_for(_pp)
        if _c: pos_pipe += sum(_e.get('pipeline', {}).values()) * 0.15 * incentive_rupees(_c)
    pipe = max(pipe, pos_pipe)
    say(f'📈 pipeline-weighted expected: ₹{pipe:,.0f}')
    say(f'   formula: 50% x 8.33% x CTC = {INC_RATE*100:.2f}% of CTC per joining')
def show_value(arg, say=print):
    rows = []
    for pp, e in _load(POS).items():
        if e.get('status') != 'open': continue
        ctc = _ctc_for(pp); n = sum(e.get('pipeline', {}).values())
        rows.append(((n * 0.15 * incentive_rupees(ctc)) if ctc else 0, e.get('idle_days', 0), n, ctc, e['client'], e['title']))
    say('🧭 open positions by expected value:')
    for exp, idle, n, ctc, cl, ti in sorted(rows, reverse=True)[:12]:
        say(f'   ₹{exp:,.0f} exp · {n} CVs · {ctc or "?"}L band · {idle}d idle · {cl} / {ti}')
def show_push(arg, say=print):
    d = _load(CASES); now = int(time.time()); acts = []
    try:
        ob = json.load(open(os.path.join(BASE, 'outbox.json'))) if os.path.exists(os.path.join(BASE, 'outbox.json')) else {'items': []}
        for i in ob['items']:
            if not i['done'] and i['due'] <= now:
                acts.append((90, f"send due {i['kind']} to {i.get('name') or i.get('phone')} (outbox)"))
    except Exception: pass
    for pp, e in _load(POS).items():
        if e.get('revisitable'):
            ctc = _ctc_for(pp)
            acts.append((70, f"revisit {e['client']} / {e['title']} - {e.get('idle_days')}d idle" + (f', ~{ctc}L band' if ctc else '')))
    for k, c in d.items():
        sts = [s['stage'].lower() for s in c.get('stages', [])]
        if sts and ('interview scheduled' in sts[-1] or 'interview cleared' in sts[-1]) and not c.get('interviews'):
            acts.append((60, f"log interview date for {c['name']} (stage: {sts[-1]})"))
    for _pp, _e in _load(POS).items():
        if _e.get('status') == 'open' and _e.get('idle_days', 0) >= 14 and sum(_e.get('pipeline', {}).values()) == 0:
            acts.append((50, f"source candidates for {_e['client']} / {_e['title']} - open {_e.get('idle_days')}d with an empty pipeline"))
    if not acts: say('🌤 no high-value pushes right now - work your due list'); return
    say('🚀 top actions by value:')
    for n, (w, t) in enumerate(sorted(acts, reverse=True)[:5], 1):
        say(f'   {n}) {t}')

def _parse_when(s):
    import datetime as _dt
    t = (s or '').strip().lower().replace('.', '')
    m = re.search(r'(\d{1,2})(?:st|nd|rd|th)?\s*([a-z]{3,9})\s*(\d{4})?\s*(?:at\s*)?(\d{1,2})?\s*(?::(\d{2}))?\s*(am|pm)?', t)
    if not m: return None
    day, mon, yr, hh, mi, ap = m.groups()
    mon = mon[:3]; yr = yr or time.strftime('%Y')
    hh = int(hh or 12); mi = int(mi or 0)
    if ap == 'pm' and hh < 12: hh += 12
    if ap == 'am' and hh == 12: hh = 0
    try:
        dt = _dt.datetime(int(yr), time.strptime(mon, '%b').tm_mon, int(day), hh, mi)
        return int(dt.timestamp())
    except Exception:
        return None
def show_digest(arg, say=print):
    import cadence, sem
    now = time.time()
    say(f'🌅 DIGEST - {time.strftime("%a %d %b")}')
    d = _load(CASES); iv = []
    for k, c in d.items():
        for s in c.get('interviews') or []:
            ts = _parse_when(s)
            if ts and time.strftime('%Y-%m-%d', time.localtime(ts)) == time.strftime('%Y-%m-%d'):
                iv.append((ts, c['name'], s, (c.get('phones') or ['?'])[0]))
    if iv:
        say('🗓 interviews today:')
        for ts, nm, s, ph in sorted(iv): say(f'   {time.strftime("%H:%M", time.localtime(ts))} · {nm} · {s} · {ph}')
    else:
        say('🗓 no interviews today (log one: interview <name> 22 Oct 2pm)')
    say('')
    cadence.show_due(say)
    say('')
    rev = [(e.get('idle_days', 0), e['client'], e['title'], _ctc_for(pp)) for pp, e in _load(POS).items() if e.get('revisitable')]
    if rev:
        say('⭐ revisitable positions (money waiting):')
        for idle, cl, ti, ctc in sorted(rev, reverse=True)[:3]:
            say(f'   {idle}d idle · {cl} / {ti}' + (f' · ~{ctc}L band · ₹{incentive_rupees(ctc):,.0f} per joining' if ctc else ''))
    sl = []
    try:
        ob = json.load(open(os.path.join(BASE, 'outbox.json')))
        sl = [x for x in ob.get('sent_log', []) if now - x.get('at', 0) < 86400]
    except Exception: pass
    say('📨 last 24h: ' + (f'{len(sl)} sent - ' + ', '.join(sorted({str(x.get("name") or x.get("phone")) for x in sl})[:6]) if sl else 'nothing sent'))
    say('')
    sem.ghost(None, None, say)
    say('')
    show_money('', say)
