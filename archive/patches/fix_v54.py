import ast, os
rep = {'butler.py': open('butler.py').read().split('\n')}
done, skipped = [], []
def P(L):
    try: ast.parse('\n'.join(L)); return True
    except Exception: return False
def ind(l): return len(l) - len(l.lstrip())
def edit(name, func):
    L = rep['butler.py']
    try: L2 = func(list(L))
    except Exception: skipped.append(name + ':anchor'); return
    if not L2 or L2 == L: skipped.append(name + ':nochange'); return
    if not P(L2): skipped.append(name + ':syntax'); return
    rep['butler.py'] = L2; done.append(name)
def e1(L):
    if '_BOOT_T = time.time()' in '\n'.join(L): return L
    i = next(k for k, l in enumerate(L) if 'let it FINISH' in l)
    L.insert(i, ind(L[i])*' ' + '_BOOT_T = time.time()')
    j = next(k for k, l in enumerate(L) if 'Scan complete' in l)
    L.insert(j+1, ind(L[j])*' ' + 'print(f"⏱ boot scan {time.time()-_BOOT_T:.1f}s · journal-skipped most of it")')
    return L
edit('boot-timing', e1)
def e2(L):
    out = [l.replace('time.sleep(20)', 'time.sleep(30)') if 'time.sleep(20)' in l else l for l in L]
    return out if out != L else L
edit('heartbeat-30s', e2)
for f in rep:
    open(f, 'w').write('\n'.join(rep[f]))
P = open('PROTOCOL.md').read()
if 'one writer per tree' not in P:
    P = P.rstrip() + '\n14. ONE writer process per folder tree (lock-enforced). Roles (rename/move/convert/compact/reconcile) are single-responsibility functions INSIDE that writer, never separate processes. Readers (chat/CLI/brief) are many and read-only except user-triggered WhatsApp sends. Maintenance scripts (repair_misplaced etc.) run only while the writer is paused. Never propose nested or disjoint second writers for speed; tune attention (events + tiered/interval walks) instead.\n'
    open('PROTOCOL.md', 'w').write(P); done.append('protocol-rule-14')
print('✅ applied:', done)
print('⏭ skipped:', skipped or 'none')
