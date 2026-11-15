import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
B0 = open('butler.py').read()
M0 = set(markers(B0.split('\n')))
B = B0.split('\n')
snap = list(B)
o0 = next(k for k, l in enumerate(B) if l.startswith('def outcome_cmd('))
o1 = next(k for k in range(o0 + 1, len(B)) if B[k].startswith('def '))
for k in range(o0, o1):
    if 'wa.send_review(ph' in B[k] and not B[k].strip().startswith('_wr'):
        B[k] = B[k].replace('wa.send_review(ph', '_wr = wa.send_review(ph', 1)
        done.append('wr-captured-loose'); break
print('🔎 outcome send and deed lines:')
for k in range(o0, o1):
    if 'wa.send_review' in B[k] or ('CINE-LINE v85.1' in B[k] and '📱' in B[k]):
        print('   |', B[k])
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
M1 = set(markers(open('butler.py').read().split('\n')))
lost = M0 - M1
if lost:
    print('⛔ witness diff:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff: 0 laws lost -', len(M0), 'before,', len(M1), 'after')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.32' not in t:
        open(AR, 'a').write('v85.32: the _wr capture re-anchored loosely (contains, not startswith) so a prefixed send line cannot escape it; the outcome region prints its send and deed lines into every receipt; S371 pins the capture inside outcome_cmd itself (S371)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S371 the deed's witness stands on the sending line itself", "'S370 the deed line reports what the window actually did", "ck('S371 the deed'+chr(39)+'s witness stands on the sending line itself', any(('_wr = wa.send_review' in l) for l in _src.split('def outcome_cmd(')[1].split(chr(10) + 'def ')[0].split(chr(10))))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
