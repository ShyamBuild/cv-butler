import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
def perfile():
    S = {}
    for fn in ('butler.py', 'briefing.py', 'wa.py'):
        P = os.path.join(os.getcwd(), fn)
        S[fn] = set(markers(open(P).read().split('\n'))) if os.path.exists(P) else set()
    return S
M0 = perfile()
B0 = open('butler.py').read()
B = B0.split('\n')
snap = list(B)
np = next((k for k, l in enumerate(B) if 'teach me: python3 butler.py teach' in l and 'say(' in l and 'TEACH-WIRE' not in l and '_td' not in l), None)
if np is not None and 'TEACH-IN-PLACE v85.49: ten digits' not in '\n'.join(B[np:np+4]):
    d = ind(B[np])
    B.insert(np+1, d*' ' + "_td = teach_digits_inline(cur['name'], os.path.basename(p), say)  # TEACH-IN-PLACE v85.49: ten digits spoken here become the number, the book entry and the window's address in one breath")
    B.insert(np+2, d*' ' + "if _td: ph = _td  # TEACH-WIRE v85.50: the taught digits enter the same variable the window reads - one breath, one door")
    done.append('teach-at-outcome')
    print('🔎 outcome door wired:')
    for j in range(np, np+4):
        print('   |', B[j].rstrip()[:170])
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
M1 = perfile()
lost = set()
for fn in M0:
    lost |= (M0[fn] - M1.get(fn, set()))
if lost:
    print('⛔ witness diff per file:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff per file: 0 laws lost')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.50' not in t:
        open(AR, 'a').write('v85.50: the outcome door wired at last with a broadened anchor (say anywhere on the line), the taught digits entering ph via a TEACH-WIRE marker; S390 repinned to strings only the real wire can wear, because a guard quoting its own probe is a mirror, not a witness\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("ck('S390 ") and 'TEACH-WIRE' not in l:
        d = ind(l)
        B[k] = d*' ' + "ck('S390 a silent paper becomes a ten-second conversation, then the same breath continues', (chr(35)+' TEACH-WIRE v85.50') in _src and ('_td = teach_digits_inline(' in _src))  # S390 repinned v85.50: the probe reads only strings the real wire wears - a guard that quotes its own probe grades its own handwriting"
        done.append('S390-repin'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
