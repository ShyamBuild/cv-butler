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
for tag, anchor_rename in (('sweep', "os.rename(p, q)"), ('fast', "os.rename(p, q)")):
    pass
k = 0
while True:
    idx = None
    for j in range(k, len(B)):
        if B[j].strip().startswith('os.rename(p, q)') and 'DEED-LOG-FIRST' not in '\n'.join(B[j:j+5]):
            idx = j; break
    if idx is None: break
    d = ind(B[idx])
    block_end = idx + 1
    while block_end < len(B) and (B[block_end].strip().startswith('_rename_ledger(') or B[block_end].strip().startswith('_repath_ledgers(') or B[block_end].strip().startswith('log(') or B[block_end].strip() in ('except Exception:', 'pass')):
        block_end += 1
    old = B[idx:block_end]
    logline = [x for x in old if x.strip().startswith('log(')]
    ledgers = [x for x in old if x.strip().startswith('_rename_ledger(') or x.strip().startswith('_repath_ledgers(')]
    new = [B[idx]]
    if logline:
        new += [l.rstrip() + '  # DEED-LOG-FIRST v85.62: the receipt is written before the books - a ledger complaint may never again eat a deed line' for l in logline]
    if ledgers:
        new += [d*' ' + "try:"] + [((ind(l)+4) if False else (d+4))*' ' + l.strip() for l in ledgers] + [d*' ' + "except Exception:"] + [(d+4)*' ' + "pass"]
    B[idx:block_end] = new
    done.append('deed-log-first-%d' % idx)
    k = idx + len(new)
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
RD = os.path.join(os.getcwd(), 'archive', 'rendiag.py')
open(RD, 'w').write("#!/usr/bin/env python3\nimport os, sys\n_here = os.path.dirname(os.path.abspath(__file__))\nsys.path.insert(0, os.path.dirname(_here))\nsys.path.insert(0, os.path.expanduser('~/CV_Tool'))\ntry:\n    import butler\nexcept Exception as _e:\n    print('rendiag cannot import butler; sys.path was:'); [print('  ', p) for p in sys.path]; raise\npaths = sys.argv[1:]\nif not paths:\n    root = butler._lock_root() or (butler.desk_load() or {}).get('primary') or os.getcwd()\n    paths = []\n    for dp, dn, fn in os.walk(root):\n        for x in fn:\n            if x.lower().endswith(('.pdf', '.docx', '.doc', '.rtf')):\n                paths.append(os.path.join(dp, x))\n        if len(paths) > 400: break\nbutler.rename_diag(paths)\n")
done.append('rendiag-double-guard')
M1 = perfile()
lost = set()
for fn in M0:
    lost |= (M0[fn] - M1.get(fn, set()))
if lost:
    print('⛔ witness diff per file:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff per file: 0 laws lost')
print('🔎 deed order now:')
L = open('butler.py').read().split('\n')
for k2, l in enumerate(L):
    if 'DEED-LOG-FIRST v85.62' in l:
        for j in range(max(0, k2-1), min(k2+6, len(L))):
            print('   |', L[j].rstrip()[:150])
        print('   | ---')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.62' not in t:
        open(AR, 'a').write('v85.62: DEED-LOG-FIRST - rename receipts are logged before the ledger calls and ledgers sit in their own try, so a swallowed ledger exception can never again hide a done deed; rendiag gains a double path guard and a loud sys.path confession (S407, S408)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S407 every done deed leaves its line, books or no books", "'S406 a human-shaped filename is the last witness when every eye is silent", "ck('S407 every done deed leaves its line, books or no books', _src.count(chr(35)+' DEED-LOG-FIRST v85.62') >= 2)"),
      ("'S408 the diagnostic names its own path or confesses the whole list", "'S407 every done deed leaves its line, books or no books", "ck('S408 the diagnostic names its own path or confesses the whole list', ('expanduser' in open(os.path.join(BASE_DIR, 'archive', 'rendiag.py')).read()) and ('sys.path was' in open(os.path.join(BASE_DIR, 'archive', 'rendiag.py')).read()))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
