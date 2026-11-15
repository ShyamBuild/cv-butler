import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
C = open('cadence.py').read().split('\n')
if 'def _collapse(' not in '\n'.join(C):
    i = next(k for k, l in enumerate(C) if l.strip().startswith('def arm('))
    C[i:i] = ["def _collapse(d):",
              "    seen = {}; keep = []",
              "    for it in d.get('items', []):",
              "        if it.get('done'):",
              "            keep.append(it); continue",
              "        k = (it.get('kind'), (it.get('name') or '').lower())",
              "        if k in seen:",
              "            j = seen[k]",
              "            if (it.get('due') or 0) >= (keep[j].get('due') or 0): keep[j] = it",
              "            continue",
              "        seen[k] = len(keep); keep.append(it)",
              "    d['items'] = keep",
              ""]
    done.append('collapse-helper')
for sig in ('def arm(', 'def process(', 'def run_outbox('):
    src = '\n'.join(C)
    if sig in src and f'{sig.strip()[:-1]}-collapse' not in done:
        i = next(k for k, l in enumerate(C) if l.strip().startswith(sig))
        j = next((k for k in range(i, min(i+25, len(C))) if C[k].strip().startswith('d = _load(')), None)
        if j is not None and '_collapse(d)' not in '\n'.join(C[i:j+3]):
            C.insert(j+1, ind(C[j])*' ' + '_collapse(d)')
            done.append(f'{sig.strip()[:-1]}-collapse')
src = '\n'.join(C); ast.parse(src); open('cadence.py', 'w').write(src)
import sys
sys.path.insert(0, '.')
import cadence
_d = cadence._load()
_n0 = len([x for x in _d.get('items', []) if not x.get('done')])
cadence._collapse(_d)
_n1 = len([x for x in _d.get('items', []) if not x.get('done')])
cadence._save(_d)
done.append(f'one-off-collapse-{_n0}-to-{_n1}')
B = open('butler.py').read().split('\n')
if "'S85 cadence never queues twins" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S84 clean_pos strips pipes" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S85 cadence never queues twins', 'def _collapse(' in _cad2 and _cad2.count('_collapse(d)') >= 3)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S85-guard')
print('✅', done)
