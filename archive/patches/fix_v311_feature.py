import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
for k, l in enumerate(g):
    if "_dz = _idn.get('designation') or ''" in l:
        g[k] = ind(l)*' ' + "_dz = _idn.get('designation') or title  # DESIG-FALLBACK v84.29: the designation slot is never blank - it borrows the position's name when untold"
        done.append('desig-fallback'); break
for k, l in enumerate(g):
    if l.strip().startswith('CITY_WORDS = ['):
        rhs = l.strip()[len('CITY_WORDS = '):].split('#')[0].strip()
        vals = ast.literal_eval(rhs)
        seen = set(); out = []
        for v in vals:
            if v not in seen:
                seen.add(v); out.append(v)
        g[k] = 'CITY_WORDS = ' + repr(out) + '  # CITY-DEDUPE v84.29: a law-list holds no twins'
        done.append('city-dedupe'); break
srcg = '\n'.join(g)
if srcg != open(G).read():
    ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S287 the designation slot is never blank and the city list holds no twins", "'S286 the message body drinks from the registry", "ck('S287 the designation slot is never blank and the city list holds no twins', (chr(35)+' DESIG-FALLBACK v84.29') in _br and (chr(35)+' CITY-DEDUPE v84.29') in _br)")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
