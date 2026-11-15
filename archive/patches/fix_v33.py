import ast
rep = {f: open(f).read().split('\n') for f in ('butler.py', 'briefing.py')}
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
edit('butler.py', 'interactive-global', lambda L: (L.insert(next(k for k, l in enumerate(L) if l.strip().startswith('VERSION =')) + 1, 'INTERACTIVE = False'), L)[1] if 'INTERACTIVE = False' not in L else L)
def e2(L):
    i = next(k for k, l in enumerate(L) if l.strip() == 'def _console(tty):')
    if 'global INTERACTIVE' in L[i+1]: return L
    L.insert(i+1, ind(L[i])*' ' + '    global INTERACTIVE')
    return L
edit('butler.py', 'console-global-decl', e2)
def e4(L):
    i = next(k for k, l in enumerate(L) if l.strip() == 'def _ask(prompt):')
    if any('INTERACTIVE = True' in l for l in L[i:i+3]): return L
    d = ind(L[i])
    L[i+1:i+3] = [d*' ' + '    global INTERACTIVE',
                  d*' ' + "    print(prompt, end='', flush=True)",
                  d*' ' + '    INTERACTIVE = True',
                  d*' ' + '    try: return tty.readline().strip()',
                  d*' ' + '    finally: INTERACTIVE = False']
    return L
edit('butler.py', 'ask-flagged', e4)
def e5(L):
    if 'def hsay(m):' in L: return L
    i = next(k for k, l in enumerate(L) if l.strip().startswith('print(f"💓 sweep #{n}'))
    d = ind(L[i]); j = i + 1
    while j < len(L) and ('_reconcile_tags' in L[j] or 'reconcile error' in L[j] or L[j].strip() in ('except Exception: pass', 'except Exception as _re: pass')):
        j += 1
    blk = [d*' ' + 'if not INTERACTIVE:', d*' ' + '    ' + L[i].strip(),
           d*' ' + 'def hsay(m):', d*' ' + '    if INTERACTIVE: log.info(m)', d*' ' + '    else: print(m)']
    for k in range(i+1, j):
        blk.append(d*' ' + '    ' + L[k].strip().replace('(print)', '(hsay)'))
    L[i:j] = blk
    return L
edit('butler.py', 'sweeps-really-silenced', e5)
def e8(L):
    i = next(k for k, l in enumerate(L) if "'S10 prompts silence sweeps'" in l)
    if 'if not INTERACTIVE:' in L[i]: return L
    L[i] = L[i].replace("'INTERACTIVE = False' in _src", "'INTERACTIVE = False' in _src and 'if not INTERACTIVE:' in _src and 'def hsay(m):' in _src")
    L[i+1:i+1] = [ind(L[i])*' ' + "ck('S11 missed works without focus + help card', \"'display': clean_pos(os.path.basename(root)),\" in _br and 'missed  <number>' in _br)"]
    return L
edit('butler.py', 'S10-strengthened+S11', e8)
def e6(L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def do_missed('))
    j = next(k for k in range(i+1, len(L)) if L[k].strip().startswith('say("set a focus first'))
    d = ind(L[j])
    L[j:j+1] = [d*' ' + "f = {'path': root, 'display': clean_pos(os.path.basename(root)),",
                d*' ' + "     'client': re.sub(r'^\\d+[\\s_-]*', '', os.path.basename(os.path.dirname(root)))}"]
    return L
edit('briefing.py', 'missed-root-fallback', e6)
def e7(L):
    i = next(k for k, l in enumerate(L) if 'missed-call WhatsApp draft' in l)
    if any('missed  <number>' in l for l in L): return L
    L.insert(i+1, ind(L[i])*' ' + 'missed  <number> <Name> .. missed-call template to a pasted number (Naukri tab - no CV needed)')
    return L
edit('briefing.py', 'help-card-missed-number', e7)
for f in rep:
    open(f, 'w').write('\n'.join(rep[f]))
print('✅ applied:', done)
print('⏭ skipped:', skipped or 'none')
