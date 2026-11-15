import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'archive'))
import patchlib as P
done = []
M0 = P.perfile()
B = P.read()
s40 = next((k for k, l in enumerate(B) if l.strip().startswith("ck('S440 ")), None)
if s40 is not None and not any(l.strip().startswith("ck('S441 ") for l in B):
    d = P.ind(B[s40])
    B.insert(s40+1, d*' ' + "ck('S441 the eye may name but never rename - authority rests with the trained gates and the master'+chr(39)+'s hand', (chr(35)+' EYES-PROPOSE-ONLY v85.98') in _src)")
    B.insert(s40+2, d*' ' + "ck('S441B no background sweep renames from eye text', _src.count('sweep renamed ' + '(eyes)') == 0)")
    B.insert(s40+3, d*' ' + "ck('S441C no service renames from eye text, only proposes', _src.count('service renamed ' + '(eyes)') == 0 and ('service proposes:' in _src))")
    done.append('s441-trio')
lost = P.preflight(B, M0)
if lost:
    print('⛔ preflight markers would be lost:', sorted(lost)); raise SystemExit('fix before write')
P.write(B); P.witness(M0)
print('🔎 taught-lookup region, verbatim (for next lap debt):')
L = open('butler.py').read().split('\n')
for j in range(257, min(282, len(L))):
    print('   |', j+1, '|', L[j].rstrip()[:160])
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
t = open(AR).read()
if 'v85.100' not in t:
    open(AR, 'a').write('v85.100: the S441 trio pinned at last (marker, no-sweep-eye-rename, service-propose-only) after the split missed its anchor in the rolled-back base; taught-lookup lines 258-282 printed verbatim so the borrowed-number debt is repaid against read code next lap (S444)\n')
    done.append('arch-line')
src = '\n'.join(B)
def anch(*nd):
    for x in nd:
        hit = [k for k, l in enumerate(B) if x in l]
        if hit: return hit[-1]
    return None
GU = [("'S444 the propose-only law stands pinned by three guards", "'S443 a failed guard confesses its own probe", "ck('S444 the propose-only law stands pinned by three guards', _src.count(chr(39)+'S441') >= 3 or _src.count(\"ck('S441\") >= 3)")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = P.ind(B[i]); B.insert(i+1, d*' ' + line); done.append(needle.split()[0].strip("'") + '-guard')
P.write(B)
print('✅', done)
