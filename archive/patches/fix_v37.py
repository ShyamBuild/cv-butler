import ast
rep = {f: open(f).read().split('\n') for f in ('wa.py', 'butler.py')}
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
def a1(L):
    if any(l.strip().startswith('AUTOSEND =') for l in L): return L
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def send_review('))
    L[i:i] = ["AUTOSEND = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', '.autosend')", '']
    return L
edit('wa.py', 'autosend-const', a1)
edit('wa.py', 'prompt-reworded', lambda L: [l.replace('[Enter] send · [e] edit msg · [n] fix number · [q] skip:', '[Enter] put in WhatsApp field (you send) · [e] edit msg · [n] fix number · [q] skip:') for l in L])
def s15(L):
    if "'S15 autosend constant defined'" in '\n'.join(L): return L
    i = next(k for k, l in enumerate(L) if "'S14 manual-send default'" in l)
    d = ind(L[i])
    L.insert(i+1, d*' ' + "ck('S15 autosend constant defined', 'AUTOSEND =' in _wa)")
    return L
edit('butler.py', 'S15-guard', s15)
for f in rep:
    open(f, 'w').write('\n'.join(rep[f]))
print('✅ applied:', done)
print('⏭ skipped:', skipped or 'none')
