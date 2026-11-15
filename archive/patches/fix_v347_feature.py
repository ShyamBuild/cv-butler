import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
snap = list(B)
for k, l in enumerate(B):
    if 'no 📱 · n = cancel ›' in l and 'he stays in the chair' not in l and 'outcome_cmd' in '\n'.join(B[max(0,k-60):k]):
        B[k] = l.replace('no 📱 · n = cancel ›', 'no 📱 · n = cancel, he stays in the chair › ')
        done.append('cue-cancel-outcome'); break
for k, l in enumerate(B):
    if 't = same, no 📱 · n = cancel ›' in l and 'nothing changes' not in l:
        B[k] = l.replace('t = same, no 📱 · n = cancel ›', 't = same, no 📱 · n = cancel, nothing changes › ')
        done.append('cue-cancel-tagvoice'); break
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:cues')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v84.54' not in t:
        open(AR, 'a').write('v84.54: the cue names what cancel leaves - n keeps the row open and remembers nothing; 7 closes the row into skips.json; t closes it with the deed but no text; y closes it with deed and draft\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S326 the cue says aloud what cancel leaves behind", "'S325 the emoji cue coexists with the banned glyph's absence", "ck('S326 the cue says aloud what cancel leaves behind', (chr(35)+' ASK-LINE v84.49') in _src and ('n = cancel, he stays in the chair' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
