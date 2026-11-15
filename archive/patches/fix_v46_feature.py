import ast
p = 'briefing.py'; L = open(p).read().split('\n'); done = []
n = 0
for k, l in enumerate(L):
    if '_pick_phone(phones_of(hit) or _phones_by_basename(hit), say)' in l:
        L[k] = l.replace('_pick_phone(phones_of(hit) or _phones_by_basename(hit), say)',
                         '_pick_phone(_phones_by_basename(hit) or phones_of(hit), say)')
        n += 1
if n: done.append(f'learned-before-extraction-x{n}')
open(p, 'w').write('\n'.join(L))
B = open('butler.py').read().split('\n')
if "'S28 learned phone beats extraction" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S27 nudge routes" in l)
    d = len(B[i]) - len(B[i].lstrip())
    B.insert(i+1, d*' ' + "ck('S28 learned phone beats extraction', '_phones_by_basename(hit) or phones_of(hit)' in _br)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S28-guard')
print('✅', done or 'nothing missing')
