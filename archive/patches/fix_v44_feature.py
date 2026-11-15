import ast
rep = {f: open(f).read().split('\n') for f in ('briefing.py', 'butler.py')}
done = []
L = rep['briefing.py']
i = next(k for k, l in enumerate(L) if l.strip().startswith('def _scan_path('))
j = i + 1
while j < len(L) and not (L[j].strip().startswith('def ') and not (len(L[j]) - len(L[j].lstrip()))): j += 1
L[i:j] = ["def _scan_path(num, root=None):",
          "    base = os.path.dirname(os.path.abspath(__file__))",
          "    names = []",
          "    if root:",
          "        names.append('scan_index_' + hashlib.md5(os.path.abspath(root).encode()).hexdigest()[:8] + '.json')",
          "    for fn in names + sorted(x for x in os.listdir(base) if x.startswith('scan_index_') and x.endswith('.json')):",
          "        try: d = json.load(open(os.path.join(base, fn)))",
          "        except Exception: continue",
          "        if root and os.path.abspath(d.get('root') or '') != os.path.abspath(root): continue",
          "        hit = (d.get('idx') or {}).get(str(num))",
          "        if hit and os.path.exists(hit): return hit",
          "    return None"]
done.append('scan-path-per-root')
rep['briefing.py'] = L
B = rep['butler.py']
if "'S26 scan index per-root only" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S25 containment refusal" in l)
    d = len(B[i]) - len(B[i].lstrip())
    B.insert(i+1, d*' ' + "ck('S26 scan index per-root only', \"scan_index_' + hashlib\" in _br and 'scan_index.json' not in _br.split('def _scan_path')[1].split('def ')[0])")
    done.append('S26-guard')
rep['butler.py'] = B
for f in rep:
    open(f, 'w').write('\n'.join(rep[f]))
print('✅', done)
