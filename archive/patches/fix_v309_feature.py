import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if l.strip().startswith("out['company'] = ov.get('company') or cm.get(client, '') or ''"):
        B[k] = ind(l)*' ' + "out['company'] = cm.get(client) or ov.get('company') or ''  # COMPANY-LIVE v84.27: the client map is the living truth; a frozen position copy never outranks it"
        done.append('company-live'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S285 the living client map outranks every frozen copy", "'S284 a re-teaching speaks its before-and-after", "ck('S285 the living client map outranks every frozen copy', (chr(35)+' COMPANY-LIVE v84.27') in _src)")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
