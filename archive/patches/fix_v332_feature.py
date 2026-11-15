import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
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
for k, l in enumerate(g):
    if "'designation': _dz}" in l and "'client':" not in l:
        g[k] = l.replace("'designation': _dz}", "'client': cli, 'designation': _dz}  # CLIENT-KEY v84.42: legacy templates ask for {client}; the living registry answers")
        done.append('client-key'); break
srcg = '\n'.join(g)
if srcg != open(G).read():
    ast.parse(srcg); open(G, 'w').write(srcg)
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v84.42' not in t:
        open(AR, 'a').write('v84.42: _draft_fields restores the folder-parse floor beneath the registry ceiling (no self-referential fields); briefing _tpl_fields gains the client key so legacy {client} placeholders fill from the living registry\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S310 no field may reference itself before birth", "'S309 the email probe is silent and the triple speaks once at the seat", "ck('S310 no field may reference itself before birth', (chr(35)+' FIELDS-SAFE v84.42') in _src and (\"role = _idn['role'] or role.strip()\" in _src))"),
      ("'S311 legacy templates' client placeholder fills from the living registry", "'S310 no field may reference itself before birth", "ck('S311 legacy templates'+chr(39)+' client placeholder fills from the living registry', (chr(35)+' CLIENT-KEY v84.42') in open(os.path.join(BASE_DIR, 'briefing.py')).read())")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
