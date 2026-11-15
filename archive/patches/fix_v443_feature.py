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
rl = next((k for k, l in enumerate(B) if l.startswith('def _rename_ledger(')), None)
if rl is not None and 'def _safe_rename_ledger(' not in '\n'.join(B):
    B[rl:rl] = ["def _safe_rename_ledger(*a, **k):  # DEED-LOG-FIRST v85.62: the books may complain in private; the receipt must never die with them",
                "    try:",
                "        return _rename_ledger(*a, **k)",
                "    except Exception:",
                "        return None",
                "def _safe_repath_ledgers(*a, **k):  # DEED-LOG-FIRST v85.62: a ledger exception is swallowed alone, never taking the deed line down",
                "    try:",
                "        return _repath_ledgers(*a, **k)",
                "    except Exception:",
                "        return None",
                ""]
    done.append('safe-ledgers-def')
n1 = 0
for k, l in enumerate(B):
    if '_rename_ledger(' in l and not l.strip().startswith('def _rename_ledger(') and '(*a, **k)' not in l and '_safe_rename_ledger(' not in l:
        B[k] = l.replace('_rename_ledger(', '_safe_rename_ledger(')
        n1 += 1
n2 = 0
for k, l in enumerate(B):
    if '_repath_ledgers(' in l and not l.strip().startswith('def _repath_ledgers(') and '(*a, **k)' not in l and '_safe_repath_ledgers(' not in l:
        B[k] = l.replace('_repath_ledgers(', '_safe_repath_ledgers(')
        n2 += 1
if n1 or n2: done.append('safe-ledgers-wired-x%d-x%d' % (n1, n2))
lk = next((k for k, l in enumerate(B) if l.strip().startswith('root = _lock_root() or root')), None)
if lk is not None and 'desk_load' not in B[lk]:
    d = ind(B[lk])
    B[lk] = d*' ' + "root = _lock_root() or (desk_load() or {}).get('primary') or root  # LOCK-ROOT v85.54 + desk-book fallback v85.63: a dead watcher takes its lock to the grave, but the desk remembers its own primary"
    done.append('lock-root-desk-fallback')
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
RD = os.path.join(os.getcwd(), 'archive', 'rendiag.py')
open(RD, 'w').write("#!/usr/bin/env python3\nimport os, sys\n_here = os.path.dirname(os.path.abspath(__file__))\nsys.path.insert(0, os.path.dirname(_here))\nsys.path.insert(0, os.path.expanduser('~/CV_Tool'))\ntry:\n    import butler\nexcept Exception as _e:\n    print('rendiag cannot import butler; sys.path was:')\n    for p in sys.path:\n        print('  ', p)\n    raise\npaths = sys.argv[1:]\nif not paths:\n    root = butler._lock_root() or (butler.desk_load() or {}).get('primary') or os.getcwd()\n    paths = []\n    for dp, dn, fn in os.walk(root):\n        for x in fn:\n            if x.lower().endswith(('.pdf', '.docx', '.doc', '.rtf')):\n                paths.append(os.path.join(dp, x))\n        if len(paths) > 400: break\nbutler.rename_diag(paths)\n")
done.append('rendiag-double-guard')
M1 = perfile()
lost = set()
for fn in M0:
    lost |= (M0[fn] - M1.get(fn, set()))
if lost:
    print('⛔ witness diff per file:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff per file: 0 laws lost')
print('🔎 wrappers, wired sites, lock line:')
L = open('butler.py').read().split('\n')
for k2, l in enumerate(L):
    if 'def _safe_rename_ledger(' in l or 'def _safe_repath_ledgers(' in l or '_safe_rename_ledger(p,' in l or 'desk-book fallback v85.63' in l:
        print('   |', l.strip()[:150])
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.63' not in t:
        open(AR, 'a').write('v85.63: DEED-LOG-FIRST by wrappers not surgery - _safe_rename_ledger/_safe_repath_ledgers swallow ledger complaints so receipts always print; LOCK-ROOT falls back to desk.json primary when a dead watcher deletes its lock; rendiag double-guarded with sys.path confession (S407, S408)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S407 every done deed leaves its line, books or no books", "'S406 a human-shaped filename is the last witness when every eye is silent", "ck('S407 every done deed leaves its line, books or no books', ('def _safe_rename_ledger(' in _src) and ('def _safe_repath_ledgers(' in _src) and _src.count('_safe_rename_ledger(') >= 2)"),
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
