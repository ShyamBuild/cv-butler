import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
C = open('cadence.py').read()
if 'def queue(name, kind, note=' in C and 'due=None' not in C.split('def queue')[1].split('def ')[0]:
    C = C.replace("def queue(name, kind, note=''):\n    d = _load(); now = int(time.time())\n    d['items'].append({'kind': kind, 'name': name, 'due': now, 'note': note, 'done': False, 'at': now})",
                  "def queue(name, kind, note='', due=None):\n    d = _load(); now = int(time.time())\n    d['items'].append({'kind': kind, 'name': name, 'due': int(due) if due else now, 'note': note, 'done': False, 'at': now})")
    open('cadence.py', 'w').write(C); done.append('cadence-queue-due')
G = open('ledger.py').read()
if 'def _parse_when(' not in G:
    G += '''
def _parse_when(s):
    import datetime as _dt
    t = (s or '').strip().lower().replace('.', '')
    m = re.search(r'(\\d{1,2})(?:st|nd|rd|th)?\\s*([a-z]{3,9})\\s*(\\d{4})?\\s*(?:at\\s*)?(\\d{1,2})?\\s*(?::(\\d{2}))?\\s*(am|pm)?', t)
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
'''
    open('ledger.py', 'w').write(G); done.append('digest')
if '# BOOKENDS v46' not in G:
    L = G.split('\n')
    i = next(k for k, l in enumerate(L) if l.strip().startswith("_save(CASES, d); say(f\"🗓 interview logged:"))
    d0 = ind(L[i])
    L[i:i+1] = [d0*' ' + '_save(CASES, d)',
                d0*' ' + '# BOOKENDS v46',
                d0*' ' + 'ts = _parse_when(parts[1])',
                d0*' ' + 'if ts:',
                d0*' ' + '    import cadence, datetime as _dt',
                d0*' ' + '    lt = time.localtime(ts)',
                d0*' ' + '    day0 = _dt.datetime(lt.tm_year, lt.tm_mon, lt.tm_mday)',
                d0*' ' + "    cadence.queue(cd['name'], 'interview_eve', note=parts[1], due=int((day0 - _dt.timedelta(hours=5, minutes=30)).timestamp()))",
                d0*' ' + "    cadence.queue(cd['name'], 'interview_morning', note=parts[1], due=int((day0 + _dt.timedelta(hours=8, minutes=30)).timestamp()))",
                d0*' ' + "    cadence.queue(cd['name'], 'interview_feedback_ask', note=parts[1], due=int((day0 + _dt.timedelta(hours=19)).timestamp()))",
                d0*' ' + "    cadence.queue(cd['name'], 'interview_nextday_chase', note=parts[1], due=int((day0 + _dt.timedelta(days=1, hours=11)).timestamp()))",
                d0*' ' + '    say(f"🗓 interview logged: {parts[1]} · bookends armed (eve, 08:30, 19:00 feedback, next-day chase)")',
                d0*' ' + 'else:',
                d0*' ' + '    say(f"🗓 interview logged: {parts[1]} (date not parseable - bookends skipped; try e.g. 22 Oct 2pm)")']
    open('ledger.py', 'w').write('\n'.join(L)); done.append('interview-bookends')
F = open('briefing.py').read().split('\n')
for k, l in enumerate(F):
    if "'recap','similar','ghost','client')" in l and "'digest'" not in l:
        F[k] = l.replace("'client')", "'client','digest')"); done.append('door-list'); break
for k, l in enumerate(F):
    if l.strip().startswith("elif cmd == 'client'"):
        F.insert(k+1, ind(l)*' ' + "elif cmd == 'digest': import ledger; ledger.show_digest(arg, print)")
        done.append('cli-digest'); break
for k, l in enumerate(F):
    if l.strip().startswith("if q.lower().startswith('client ')"):
        F.insert(k+1, ind(l)*' ' + "if q.lower().startswith('digest'): import ledger; ledger.show_digest(q[6:].strip()); continue")
        done.append('chat-digest'); break
new = '\n'.join(F); ast.parse(new); open('briefing.py', 'w').write(new)
B = open('butler.py').read().split('\n')
if "'S48 digest + bookends" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S47 ghost reads conversations only" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "_led4 = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ledger.py')).read() if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ledger.py')) else ''")
    B.insert(i+2, d*' ' + "ck('S48 digest + bookends', 'def show_digest(' in _led4 and 'interview_eve' in _led4 and \"cmd == 'digest'\" in _br)")
    B.insert(i+3, d*' ' + "_cad2 = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cadence.py')).read() if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cadence.py')) else ''")
    B.insert(i+4, d*' ' + "ck('S49 cadence queue accepts due', 'due=None' in _cad2)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S48-S49-guards')
print('✅', done)
