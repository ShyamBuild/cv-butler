import ast, os, re
done = []
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
GI = os.path.join(os.getcwd(), '.gitignore')
gi = open(GI).read() if os.path.exists(GI) else ''
need = ['archive/rendiag.py', '.converted.json', '.phonebook.json', '.idcache.json', '.tick.pid', '.tick.lock', 'tick.log', '.rename_queue', '.wa_status']
add = [x for x in need if x not in gi.split('\n')]
if add:
    open(GI, 'a').write('\n'.join(add) + '\n')
    done.append('gitignore-shelter-x%d' % len(add))
RD = os.path.join(os.getcwd(), 'archive', 'rendiag.py')
if not os.path.exists(RD):
    open(RD, 'w').write("#!/usr/bin/env python3\nimport os, sys\nsys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\nimport butler\npaths = sys.argv[1:]\nif not paths:\n    root = butler._lock_root() or (butler.desk_load() or {}).get('primary') or os.getcwd()\n    paths = []\n    for dp, dn, fn in os.walk(root):\n        for x in fn:\n            if x.lower().endswith(('.pdf', '.docx', '.doc', '.rtf')):\n                paths.append(os.path.join(dp, x))\n        if len(paths) > 400: break\nbutler.rename_diag(paths)\n")
    done.append('rendiag-reborn')
print('🔎 shelter and file:')
print('   |', RD, os.path.exists(RD))
for l in open(GI).read().split('\n')[-12:]:
    if l.strip(): print('   |', l)
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
    if 'v85.60' not in t:
        open(AR, 'a').write('v85.60: the broom reads the ignore-list, not the map - archive/rendiag.py and every runtime book are named in .gitignore so git clean passes over them; the diagnostic reborn beside its shelter; a file-free inline command offered as the unblockable route (S404)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S404 the broom passes over what the ignore-list names", "'S403 the bell is owned by a pulse, and orphans inherit nothing but silence", "ck('S404 the broom passes over what the ignore-list names', ('archive/rendiag.py' in open(os.path.join(BASE_DIR, '.gitignore')).read()) and os.path.exists(os.path.join(BASE_DIR, 'archive', 'rendiag.py')))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
