import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
srcg = '\n'.join(g)
if 'REGISTRY-VOICE' not in srcg:
    for k, l in enumerate(g):
        if l.strip().startswith('title, loc = _split_pos(pos)'):
            d = ind(l)
            g.insert(k+1, d*' ' + "try:  # REGISTRY-VOICE v84.28: the taught truths outrank the path guesses inside the message itself")
            g.insert(k+2, d*' ' + "    import butler as _bt")
            g.insert(k+3, d*' ' + "    _idn = _bt.pos_identity(str(hit)) if (hit and os.path.isfile(str(hit))) else {}")
            g.insert(k+4, d*' ' + "    if _idn.get('company'): cli = _idn['company']")
            g.insert(k+5, d*' ' + "    if _idn.get('role'): title = _idn['role']")
            g.insert(k+6, d*' ' + "    if _idn.get('loc'): loc = _idn['loc']")
            g.insert(k+7, d*' ' + "    _dz = _idn.get('designation') or ''")
            g.insert(k+8, d*' ' + "except Exception:")
            g.insert(k+9, d*' ' + "    _dz = ''")
            done.append('registry-voice'); break
    srcg = '\n'.join(g)
if "'bhopal'," not in srcg:
    for k, l in enumerate(g):
        if l.strip().startswith('CITY_WORDS = ['):
            g[k] = l.replace("CITY_WORDS = ['greater noida',", "CITY_WORDS = ['bhopal', 'indore', 'surat', 'chandigarh', 'greater noida',", 1)
            done.append('city-words'); break
    srcg = '\n'.join(g)
n = 0
for k, l in enumerate(g):
    if 'where_line=where, where=at)' in l and 'designation=' not in l:
        g[k] = l.replace('where_line=where, where=at)', 'where_line=where, where=at, designation=_dz)')
        n += 1
if n: done.append(f'designation-placeholders-x{n}')
srcg = '\n'.join(g)
if 'REGISTRY-VOICE' in srcg and '_dz = _idn.get' not in srcg:
    raise SystemExit('registry block incomplete')
if srcg != open(G).read():
    ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for nn in needles:
        hit = [k for k, l in enumerate(B) if nn in l]
        if hit: return hit[-1]
    return None
GU = [("'S286 the message body drinks from the registry", "'S285 the living client map outranks every frozen copy", "ck('S286 the message body drinks from the registry', (chr(35)+' REGISTRY-VOICE v84.28') in _br and ('designation=' in _br))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
