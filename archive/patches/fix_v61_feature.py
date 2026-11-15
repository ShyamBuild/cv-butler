import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
C = open('cadence.py').read()
if 'def run_outbox(' not in C:
    C += '''
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
            want = 'reference' if i['kind'] == 'reference_ask' else 'outbox'
            hitf = [f for f in sorted(os.listdir(tdir)) if want in f.lower()]
            tpl = open(os.path.join(tdir, hitf[0])).read().strip() if hitf else None
        except Exception: tpl = None
        base = tpl or (DEF_REF if i['kind'] == 'reference_ask' else DEF_ACK)
        try:
            f = briefing._read_focus() or {}
            text = base.format(name=(nm.title() or 'there'), position=f.get('display', 'your application'), company=f.get('client', 'Sunsoft Technology'))
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
'''
    open('cadence.py', 'w').write(C); done.append('run-outbox')
F = open('briefing.py').read().split('\n')
for k, l in enumerate(F):
    if l.strip() == "elif cmd == 'outbox': import cadence; cadence.show_outbox(print)":
        F[k] = ind(l)*' ' + "elif cmd == 'outbox': import cadence; cadence.run_outbox(root, print)"
        done.append('cli-outbox-send'); break
for k, l in enumerate(F):
    if l.strip() == "if q.lower().startswith('outbox'): import cadence; cadence.show_outbox(); continue":
        F[k] = ind(l)*' ' + "if q.lower().startswith('outbox'): import cadence; cadence.run_outbox(root); continue"
        done.append('chat-outbox-send'); break
new = '\n'.join(F); ast.parse(new); open('briefing.py', 'w').write(new)
B = open('butler.py').read().split('\n')
if "'S41 outbox approve-and-send" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S40 learned beats extraction" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S41 outbox approve-and-send', os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cadence.py')) and 'def run_outbox(' in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cadence.py')).read() and 'run_outbox(root' in _br)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S41-guard')
print('✅', done)
