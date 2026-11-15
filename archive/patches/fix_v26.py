import ast
rep = {f: open(f).read().split('\n') for f in ('butler.py', 'briefing.py', 'wa.py')}
done, skipped = [], []
def P(L):
    try: ast.parse('\n'.join(L)); return True
    except Exception: return False
def ind(l): return len(l) - len(l.lstrip())
def edit(fn_, name, func):
    L = rep[fn_]
    try: L2 = func(list(L))
    except Exception: skipped.append(name + ':anchor'); return
    if not L2 or L2 == L: skipped.append(name + ':nochange'); return
    if not P(L2): skipped.append(name + ':syntax'); return
    rep[fn_] = L2; done.append(name)
def cut0(L, i):
    d = ind(L[i]); j = i + 1
    while j < len(L):
        s = L[j]
        if s.strip() and ind(s) <= d and (s.lstrip().startswith('def ') or s.lstrip().startswith('class ')): break
        j += 1
    return j
GOTO = ['def _goto(page, url, say=print):', '    for a in (0, 1):', '        try:', "            page.goto(url, timeout=90000, wait_until='domcontentloaded'); return True", '        except Exception:', '            if a == 0: time.sleep(2)', "    say('⚠️ WhatsApp page did not load (network?) - try again in a minute')", '    return False', '']
def w1(L):
    if 'def _goto(' in L: return L
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def send_review('))
    L[i:i] = GOTO
    return L
edit('wa.py', 'wa-goto-helper', w1)
def b1(L):
    i = next(k for k, l in enumerate(L) if l.strip() == 'try: raw = tty.readline().strip(); line = raw.lower()')
    j = i + 1
    while j < len(L) and L[j].strip() != 'except Exception: return': j += 1
    d = ind(L[i])
    L[i:j+1] = [d*' ' + 'INTERACTIVE = True',
                d*' ' + 'try:',
                d*' ' + '    raw = tty.readline().strip(); line = raw.lower()',
                d*' ' + 'except Exception:',
                d*' ' + '    INTERACTIVE = False',
                d*' ' + '    return',
                d*' ' + 'INTERACTIVE = False']
    return L
if 'INTERACTIVE = True' not in '\n'.join(rep['butler.py']):
    edit('butler.py', 'console-read-flagged', b1)
def b2(L):
    tgt = "open(os.path.join(BASE_DIR, 'scan_index.json'), 'w')"
    if not any(tgt in l for l in L): return L
    return [l.replace(tgt, 'open(_idx_path(self.root), \'w\')') for l in L]
edit('butler.py', 'save-idx-per-root', b2)
def b3(L):
    if "'S7 wa interactive" in '\n'.join(L): return L
    i = next(k for k, l in enumerate(L) if "'S6 watcher handler intact'" in l)
    dd = ind(L[i])
    L[i+1:i+1] = [dd*' ' + "_wa = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wa.py')).read()",
                  dd*' ' + "_br = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'briefing.py')).read()",
                  dd*' ' + "_src = '\\n'.join(_ln)",
                  dd*' ' + "ck('S7 wa interactive uses _click_send', 'sent = _click_send(page)' in _wa)",
                  dd*' ' + "ck('S8 scan index per-root', 'def _scan_path(num, root=None)' in _br)",
                  dd*' ' + "ck('S9 rename swallows vanished files', 'except FileNotFoundError:' in _src)",
                  dd*' ' + "ck('S10 prompts silence sweeps', 'INTERACTIVE = False' in _src)"]
    return L
edit('butler.py', 'selftest-S7-S10', b3)
HELP = ['def _idx_path(root):', '    import hashlib', "    return os.path.join(BASE_DIR, 'scan_index_' + hashlib.md5(os.path.abspath(root).encode()).hexdigest()[:8] + '.json')", '',
        'def _phone_first(arg):', "    m = re.match(r'^\\s*(\\d{10}|\\d{12})\\b\\s*(.*)$', arg or '', re.S)", '    if not m: return None, arg', '    d = m.group(1)', "    if len(d) == 10: d = '91' + d", '    return d, m.group(2).strip()', '']
def f1(L):
    if 'def _phone_first' in L: return L
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def _scan_path('))
    L[i:i] = HELP
    return L
edit('briefing.py', 'briefing-helpers', f1)
def f2(L):
    if 'def _scan_path(num, root=None):' in '\n'.join(L): return L
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def _scan_path('))
    L[i:cut0(L, i)] = ['def _scan_path(num, root=None):', '    cands = []', '    if root: cands.append(_idx_path(root))', "    cands.append(os.path.join(BASE_DIR, 'scan_index.json'))", '    for c in cands:', '        try:', '            d = json.load(open(c))', "            if root and d.get('root') and os.path.abspath(d['root']) != os.path.abspath(root): continue", "            p = d.get('idx', {}).get(str(num))", '            if p and os.path.exists(p): return p', '        except Exception:', '            pass', '    return None', '']
    return L
edit('briefing.py', 'scan-path-per-root', f2)
def f3(L):
    out = L
    for a, b in (('_scan_path(arg.strip())', '_scan_path(arg.strip(), root)'), ('_scan_path(toks[0])', '_scan_path(toks[0], root)'), ('_scan_path(q.strip())', '_scan_path(q.strip(), root)')):
        out = [l.replace(a, b) for l in out]
    return out
if '_scan_path(arg.strip(), root)' not in '\n'.join(rep['briefing.py']):
    edit('briefing.py', 'scan-callers-root', f3)
def f4(L):
    tgt = "open(os.path.join(BASE_DIR, 'scan_index.json'), 'w')"
    if not any(tgt in l for l in L): return L
    return [l.replace(tgt, "open(_idx_path(root), 'w')") for l in L]
edit('briefing.py', 'do-list-per-root', f4)
for f in rep:
    open(f, 'w').write('\n'.join(rep[f]))
s = open('ship.sh').read()
s2 = s.replace('git checkout -- butler.py briefing.py', 'git checkout -- butler.py briefing.py wa.py cleaner.py')
if s2 != s:
    open('ship.sh', 'w').write(s2); done.append('rollback-covers-wa+cleaner')
print('✅ applied:', done)
print('⏭ skipped:', skipped or 'none')
