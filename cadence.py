import os, re, json, time, datetime
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, 'outbox.json'); CFG = os.path.join(BASE, 'fit_weights.json')
def _cfg():
    try: d = json.load(open(CFG))
    except Exception: d = {}
    d.setdefault('ack_min', 10); d.setdefault('eod_cutoff', '16:30')
    return d
def _load():
    try: return json.load(open(OUT))
    except Exception: return {'items': [], 'sent_log': []}
def _save(d):
    t = OUT + '.tmp'; json.dump(d, open(t, 'w'), indent=2); os.replace(t, OUT)
def _eod_ts(cfg):
    h, m = [int(x) for x in str(cfg['eod_cutoff']).split(':')]
    t = time.localtime()
    return int(datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday, h, m).timestamp())
def arm(phone, name):
    d = _load(); cfg = _cfg(); now = int(time.time())
    d['items'].append({'kind': 'ack_check', 'name': name, 'phone': phone, 'due': now + cfg['ack_min'] * 60, 'done': False, 'at': now})
    d['items'].append({'kind': 'eod_nudge', 'name': name, 'phone': phone, 'due': _eod_ts(cfg), 'done': False, 'at': now})
    d['sent_log'].append({'name': name, 'phone': phone, 'at': now})
    _save(d)
def queue(name, kind, note='', due=None):
    d = _load(); now = int(time.time())
    d['items'].append({'kind': kind, 'name': name, 'due': int(due) if due else now, 'note': note, 'done': False, 'at': now})
    _save(d)
def process(B, say=lambda m: None):
    d = _load(); now = int(time.time()); ch = False
    try:
        from butler import StageLog
        slog = StageLog(B.root)
        for k, rows in slog.data.items():
            if not rows: continue
            st = (rows[-1].get('stage') or '').lower()
            if (st.startswith('rejected') or st.startswith('closed')) and not any(i.get('kind') == 'reference_ask' and (i.get('name') or '').lower() == k for i in d['items']):
                d['items'].append({'kind': 'reference_ask', 'name': k.title(), 'due': now, 'note': rows[-1].get('stage', ''), 'done': False, 'at': now}); ch = True
    except Exception: pass
    due = [i for i in d['items'] if not i['done'] and i['due'] <= now]
    if due: say(f"📬 {len(due)} follow-up(s) due - type: due  (approve via: outbox)")
    if ch: _save(d)
def _fmt(i, now):
    who = i.get('name') or i.get('phone') or '?'
    return f"  ⏰ {i['kind']:<14} · {who} · {i.get('note', '')} · overdue {(now - i['due']) // 60}m" if i['due'] <= now else f"  ⏳ {i['kind']:<14} · {who} · in {(i['due'] - now) // 60}m"
def show_due(say=print):
    d = _load(); now = int(time.time())
    rows = [i for i in d['items'] if not i['done'] and i['due'] <= now + 3600]
    if not rows: say('📭 nothing due in the next hour'); return
    for i in sorted(rows, key=lambda x: x['due']): say(_fmt(i, now))
def show_outbox(say=print):
    d = _load(); now = int(time.time())
    due = [i for i in d['items'] if not i['done'] and i['due'] <= now]
    if not due: say('📭 outbox empty - nothing due right now'); return
    say(f'📤 {len(due)} due follow-up(s):')
    for n, i in enumerate(due, 1):
        say(f"{n}) {i['kind']} · {i.get('name') or i.get('phone')} · {i.get('note', '')}")
        say(f"     ready command: wa \"{i.get('name') or i.get('phone')}\" <your words>   (or: missed {i.get('name') or ''})")
def ack(arg, say=print):
    d = _load(); k = (arg or '').strip().lower(); n = 0
    for i in d['items']:
        if i['kind'] == 'ack_check' and not i['done'] and k and (k in (i.get('name') or '').lower() or (k.isdigit() and k in re.sub(r'\D', '', str(i.get('phone') or '')))):
            i['done'] = True; n += 1
    _save(d)
    say(f'✅ ack logged for {arg or "?"} - {n} ack_check(s) closed' if n else f'no open ack_check for {arg or "?"}')

DEF_ACK = "Hi {name}, following up on my last message regarding the {position} opening at {company} - please do share an update when convenient. - Sunsoft Technology"
DEF_REF = "Hi {name}, thank you for the update. If you know 1-2 colleagues who might fit similar roles, a referral would mean a lot. - Sunsoft Technology"
def run_outbox(root, say=print, ask=None):
    d = _load(); now = int(time.time())
    due = [i for i in d['items'] if not i['done'] and i['due'] <= now]
    if not due: say('📭 outbox empty - nothing due right now'); return
    say(f'📤 {len(due)} due follow-up(s):')
    for n, i in enumerate(due, 1):
        say(f"{n}) {i['kind']} · {i.get('name') or i.get('phone')} · {i.get('note', '')}")
    raw = (ask or input)('   send which? (comma list / S = all / Enter = skip): ').strip()
    if not raw: say('skipped - items stay due'); return
    sel = due if raw.lower() == 's' else [due[int(x)-1] for x in raw.split(',') if x.strip().isdigit() and 1 <= int(x) <= len(due)]
    import briefing
    sent = 0
    for i in sel:
        nm = i.get('name') or ''; ph = i.get('phone') or ''
        if not ph:
            try:
                cs = json.load(open(os.path.join(BASE, 'cases.json'))) if os.path.exists(os.path.join(BASE, 'cases.json')) else {}
                hit = next((v for k, v in cs.items() if nm and (k == nm.lower() or nm.lower() in k)), None)
                ph = (hit or {}).get('phones', [''])[0] if hit else ''
            except Exception: ph = ''
        if not ph: say(f'   ⚠️ {nm or "?"}: no phone on file - skipped'); continue
        tdir = os.path.join(BASE, 'templates'); tpl = None
        try:
            KIND_TPL = {'reference_ask': 'reference', 'interview_eve': 'interview', 'interview_morning': 'interview', 'interview_feedback_ask': 'feedback', 'interview_nextday_chase': 'feedback'}
            want = KIND_TPL.get(i['kind'], 'outbox')
            hitf = [f for f in sorted(os.listdir(tdir)) if want in f.lower()]
            tpl = open(os.path.join(tdir, hitf[0])).read().strip() if hitf else None
        except Exception: tpl = None
        base = tpl or (DEF_REF if i['kind'] == 'reference_ask' else DEF_ACK)
        try:
            f = briefing._read_focus() or {}
            text = briefing._fmt_tpl(base, (briefing._hits_for(nm, root) or [None])[0], f, (nm.title() or 'there'))
        except Exception:
            text = base
        try:
            import wa
            if wa.send_review(ph, text, say, ask=ask):
                i['done'] = True; sent += 1
        except Exception as e:
            say(f'   ⚠️ whatsapp failed: {e}')
    _save(d)
    say(f'✅ {sent} sent · the rest remain in outbox')
