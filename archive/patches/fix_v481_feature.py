import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'archive'))
import patchlib as P
done = []
M0 = P.perfile()
B = P.read()
a = next((k for k, l in enumerate(B) if '_en = _eyename_of(p)' in l), None)
if a is not None:
    b = next(k for k in range(a, min(a+30, len(B))) if 'ws = stem.split()' in B[k])
    print('🔎 deleting sweep eye block, verbatim:')
    for j in range(a, b): print('   |', B[j].rstrip()[:130])
    del B[a:b]
    done.append('sweep-eye-removed')
c = next((k for k, l in enumerate(B) if "os.rename(p, q2); log('✏️ service renamed (eyes)" in l), None)
if c is not None:
    print('🔎 service eye-rename neighbourhood before rewrite:')
    for j in range(c-1, min(c+6, len(B))): print('   |', B[j].rstrip()[:130])
    B[c] = P.ind(B[c])*' ' + "log('🧭 service proposes: %s reads as %s in its head - rename in Finder or teach me; the eye may name but never rename' % (x, d2))  # EYES-PROPOSE-ONLY v85.98: authority returns to the trained gates and the master's hand"
    k = c+1
    while k < len(B) and not B[k].strip().startswith('except Exception as _se2'):
        k += 1
    del B[c+1:k]
    done.append('service-eye-proposal')
n = P.sub_in_line(B, "_EYE_VSN = 'v85.97'", "_EYE_VSN = 'v85.98'", 'EYES-PROPOSE-ONLY v85.98: cached slogan verdicts expire with the authority that made them')
if n: done.append('eyevsn-bump')
lost = P.preflight(B, M0)
if lost:
    print('⛔ preflight markers would be lost:', sorted(lost)); raise SystemExit('fix before write')
P.write(B)
P.witness(M0)
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
t = open(AR).read()
if 'v85.98' not in t:
    open(AR, 'a').write('v85.98: EYES-PROPOSE-ONLY - the background sweep no longer renames from eye text at all (case-fix only), and the right-click turns eye-names into spoken proposals; wrapped CV line fragments made every line-scanning guess unsafe, and the trained ceremony gates remain the only renaming authority beside the master hand; S441 forbids the eye-rename strings forever (S441)\n')
    done.append('arch-line')
src = '\n'.join(B)
def anch(*nd):
    for x in nd:
        hit = [k for k, l in enumerate(B) if x in l]
        if hit: return hit[-1]
    return None
GU = [("'S441 the eye may name but never rename - authority rests with the trained gates and the master's hand", "'S440 a motto never wears a man's coat", "ck('S441 the eye may name but never rename - authority rests with the trained gates and the master'+chr(39)+'s hand', (chr(35)+' EYES-PROPOSE-ONLY v85.98') in _src and ('sweep renamed (eyes)' not in _src) and ('service renamed (eyes)' not in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = P.ind(B[i]); B.insert(i+1, d*' ' + line); done.append(needle.split()[0].strip("'") + '-guard')
P.write(B)
print('✅', done)
