import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
G = open('ledger.py').read()
if 'def show_money(' not in G:
    G += '''
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
            try: ctc = float(re.sub(r'[^\\d.]', '', str(o.get('ctc', '')) or '0') or 0)
            except Exception: ctc = 0.0
        sts = [s['stage'].lower() for s in c.get('stages', [])]
        sel = c.get('joining') or any('join' in s or 'payment' in s for s in sts)
        if o and ctc and sel:
            realized += incentive_rupees(ctc); n_sel += 1
        elif sts:
            est = ctc or (_ctc_for(c['positions'][-1]) if c.get('positions') else None)
            if est: pipe += _p_join(sts[-1]) * incentive_rupees(est)
    say(f'💰 realized (selections with offers): ₹{realized:,.0f} across {n_sel} selection(s)')
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
    if not acts: say('🌤 no high-value pushes right now - work your due list'); return
    say('🚀 top actions by value:')
    for n, (w, t) in enumerate(sorted(acts, reverse=True)[:5], 1):
        say(f'   {n}) {t}')
'''
    open('ledger.py', 'w').write(G); done.append('money-brain')
F = open('briefing.py').read().split('\n')
for k, l in enumerate(F):
    if "'offer','due','outbox','ack')" in l and "'money'" not in l:
        F[k] = l.replace("'ack')", "'ack','money','value','push')"); done.append('door-list'); break
for k, l in enumerate(F):
    if l.strip().startswith("elif cmd == 'ack'"):
        F.insert(k+1, ind(l)*' ' + "elif cmd == 'money': import ledger; ledger.show_money(arg, print)")
        F.insert(k+2, ind(l)*' ' + "elif cmd == 'value': import ledger; ledger.show_value(arg, print)")
        F.insert(k+3, ind(l)*' ' + "elif cmd == 'push': import ledger; ledger.show_push(arg, print)")
        done.append('cli-money-routes'); break
for k, l in enumerate(F):
    if "startswith('ack ')" in l and 'ledger' not in l:
        F.insert(k+1, ind(l)*' ' + "if q.lower().startswith('money'): import ledger; ledger.show_money(q[5:].strip()); continue")
        F.insert(k+2, ind(l)*' ' + "if q.lower().startswith('value'): import ledger; ledger.show_value(q[5:].strip()); continue")
        F.insert(k+3, ind(l)*' ' + "if q.lower().startswith('push'): import ledger; ledger.show_push(q[4:].strip()); continue")
        done.append('chat-money-routes'); break
new = '\n'.join(F); ast.parse(new); open('briefing.py', 'w').write(new)
B = open('butler.py').read().split('\n')
if "'S42 money brain" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S41 outbox approve-and-send" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "_led2 = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ledger.py')).read() if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ledger.py')) else ''")
    B.insert(i+2, d*' ' + "ck('S42 money brain routed', 'def show_money(' in _led2 and \"cmd == 'money'\" in _br)")
    B.insert(i+3, d*' ' + "ck('S43 incentive formula constant', ('INC_RATE = 0.5 * 0.0833') in _led2)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S42-S43-guards')
print('✅', done)
