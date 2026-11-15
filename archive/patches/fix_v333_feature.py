import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
c0 = next(k for k, l in enumerate(B) if l.startswith('def calls_cmd('))
c1 = next(k for k in range(c0 + 1, len(B)) if B[k].startswith('def sheet_cmd('))
mis = [k for k in range(c0, c1) if B[k].strip().startswith('if _in_nonqueue(p): continue')]
if mis:
    k = mis[0]
    pj = next(j for j in range(k, c1) if B[j].strip().startswith('p = os.path.join(dp, x)'))
    del B[k]
    pj2 = next(j for j in range(c0, c1) if B[j].strip().startswith('p = os.path.join(dp, x)'))
    B.insert(pj2 + 1, ind(B[pj2])*' ' + "if _in_nonqueue(p): continue  # NON-QUEUE v84.39 (moved v84.43): a check stands after the path it reads is born, never before")
    done.append('nonqueue-moved')
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip() == "role = _idn['role'] or role" and B[k+1].strip() == "loc = _idn['loc'] or loc":
        d = ind(l)
        B[k:k+2] = [d*' ' + "role, loc = (pos.split(' -', 1) + [''])[:2] if pos else ('', '')  # FIELDS-SAFE v84.42: the folder parse is the floor; the registry is the ceiling - no field may reference itself before birth",
                    d*' ' + "role = _idn['role'] or role.strip()",
                    d*' ' + "loc = _idn['loc'] or loc.strip()"]
        done.append('fields-safe'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
n = 0
for k, l in enumerate(g):
    if 'where=at, designation=_dz)' in l and 'client=cli' not in l:
        g[k] = l.replace('where=at, designation=_dz)', 'where=at, designation=_dz, client=cli)  # CLIENT-KEY v84.42: legacy templates ask for {client}; the living registry answers')
        n += 1
if n: done.append('client-key-x%d' % n)
srcg = '\n'.join(g)
if srcg != open(G).read():
    ast.parse(srcg); open(G, 'w').write(srcg)
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v84.43' not in t:
        open(AR, 'a').write('v84.43: the nonqueue check stands after the path is born (S312 pins the order); client=cli joins both _fmt_tpl format calls; fields-safe restored\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n2 in needles:
        hit = [k for k, l in enumerate(B) if n2 in l]
        if hit: return hit[-1]
    return None
GU = [("'S310 no field may reference itself before birth", "'S309 the email probe is silent and the triple speaks once at the seat", "ck('S310 no field may reference itself before birth', (chr(35)+' FIELDS-SAFE v84.42') in _src and (\"role = _idn['role'] or role.strip()\" in _src))"),
      ("'S311 legacy templates' client placeholder fills from the living registry", "'S310 no field may reference itself before birth", "ck('S311 legacy templates'+chr(39)+' client placeholder fills from the living registry', (chr(35)+' CLIENT-KEY v84.42') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and ('client=cli' in open(os.path.join(BASE_DIR, 'briefing.py')).read()))"),
      ("'S312 a check never stands before the path it reads is born", "'S311 legacy templates' client placeholder fills from the living registry", "ck('S312 a check never stands before the path it reads is born', (lambda seg: seg.find('_in_nonqueue(p)') > seg.find('p = os.path.join(dp, x)') >= 0)(_src.split('def calls_cmd(')[1].split('def sheet_cmd(')[0]))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
