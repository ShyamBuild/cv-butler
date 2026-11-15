import ast
CAD = '''import os, json, time, datetime
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
def queue(name, kind, note=''):
    d = _load(); now = int(time.time())
    d['items'].append({'kind': kind, 'name': name, 'due': now, 'note': note, 'done': False, 'at': now})
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
        say(f"     ready command: wa \\"{i.get('name') or i.get('phone')}\\" <your words>   (or: missed {i.get('name') or ''})")
def ack(arg, say=print):
    d = _load(); k = (arg or '').strip().lower(); n = 0
    for i in d['items']:
        if i['kind'] == 'ack_check' and not i['done'] and k and k in (i.get('name') or '').lower():
            i['done'] = True; n += 1
    _save(d)
    say(f'✅ ack logged for {arg or "?"} - {n} ack_check(s) closed' if n else f'no open ack_check for {arg or "?"}')
'''
open('cadence.py', 'w').write(CAD)
rep = {f: open(f).read().split('\n') for f in ('butler.py', 'briefing.py')}
done = ['cadence-module']
def ind(l): return len(l) - len(l.lstrip())
B = rep['butler.py']
if 'cadence.process(B' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if 'import ledger; ledger.tick(B)' in l)
    B.insert(i+1, ind(l)*' ' + 'import cadence; cadence.process(B, hsay)')
    done.append('heartbeat-cadence')
if "'S37 cadence armed" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S36 StageLog not self-recursive" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S37 cadence armed + processed', 'cadence.arm(' in _br and 'cadence.process(B' in _src)")
    B.insert(i+2, d*' ' + "ck('S38 outbox/due/ack routed', \"cmd == 'outbox'\" in _br)")
    done.append('S37-S38-guards')
rep['butler.py'] = B
F = rep['briefing.py']
idxs = [k for k, l in enumerate(F) if 'fitrank.mark_called(hit)' in l or 'fitrank.mark_called(os.path.join(folder, x))' in l]
for k in reversed(idxs):
    F.insert(k+1, ind(F[k])*' ' + 'try: import cadence; cadence.arm(phone, os.path.splitext(os.path.basename(hit if "mark_called(hit)" in "' + '' + '" or True else hit))[0])')
    F.insert(k+2, ind(F[k])*' ' + 'except Exception: pass')
done.append(f'cadence-arm-x{len(idxs)}')
for k, l in enumerate(F):
    if "'note','interview','offer')" in l and "'due'" not in l:
        F[k] = l.replace("'offer')", "'offer','due','outbox','ack')"); done.append('door-list'); break
for k, l in enumerate(F):
    if l.strip().startswith("elif cmd == 'offer'"):
        F.insert(k+1, ind(l)*' ' + "elif cmd == 'due': import cadence; cadence.show_due(print)")
        F.insert(k+2, ind(l)*' ' + "elif cmd == 'outbox': import cadence; cadence.show_outbox(print)")
        F.insert(k+3, ind(l)*' ' + "elif cmd == 'ack': import cadence; cadence.ack(arg, print)")
        done.append('cli-cadence-routes'); break
for k, l in enumerate(F):
    if "startswith('positions')" in l and 'cadence' not in l:
        F.insert(k+1, ind(l)*' ' + "if q.lower().startswith('due'): import cadence; cadence.show_due(); continue")
        F.insert(k+2, ind(l)*' ' + "if q.lower().startswith('outbox'): import cadence; cadence.show_outbox(); continue")
        F.insert(k+3, ind(l)*' ' + "if q.lower().startswith('ack '): import cadence; cadence.ack(q[4:].strip()); continue")
        done.append('chat-cadence-routes'); break
rep['briefing.py'] = F
for f in rep:
    new = '\n'.join(rep[f]); ast.parse(new); open(f, 'w').write(new)
print('✅', done)
