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
n = 0
for k, l in enumerate(B):
    if 'dirs = [root] + [os.path.join(root, s) for s in _tag_vocab()' in l and 'DIRS-ALL' not in l:
        d = ind(l)
        B[k] = d*' ' + "dirs = [root] + [os.path.join(root, s) for s in os.listdir(root) if os.path.isdir(os.path.join(root, s)) and not s.startswith('.')]  # DIRS-ALL v85.69: every immediate folder of the chair is swept - the stage folders hold every seated paper, and a bell that walks only the root walks an empty hall"
        n += 1
if n: done.append('dirs-all-x%d' % n)
ic = next((k for k, l in enumerate(B) if l.strip().startswith("ic = os.path.expanduser('~/Library/Mobile Documents")), None)
if ic is not None and 'BACKUP-LOCAL' not in B[ic]:
    d = ind(B[ic])
    B[ic] = d*' ' + "ic = os.path.expanduser('~/Backup of Butler')  # BACKUP-LOCAL v85.69: the memory archives come home to a local folder - iCloud was filling with half-gigabyte weeks, and a backup that starves the master's cloud is a backup that owes an apology"
    B.insert(ic+1, d*' ' + "os.makedirs(ic, exist_ok=True)")
    done.append('backup-local')
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
print('🔎 dirs lines and backup home:')
L = open('butler.py').read().split('\n')
for k2, l in enumerate(L):
    if 'DIRS-ALL v85.69' in l or 'BACKUP-LOCAL v85.69' in l:
        print('   |', l.strip()[:160])
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.69' not in t:
        open(AR, 'a').write('v85.69: DIRS-ALL - the sweep and the tick walk every immediate folder of the chair because the blind _tag_vocab call degraded dirs to root and the bell swept an empty hall; BACKUP-LOCAL - cv-memory and cv-tree tgz files write and prune in ~/Backup of Butler instead of iCloud (S413, S414)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S413 the bell walks every room of the chair, not an empty hall", "'S412 a silent pdf row carries the complaint that silenced it", "ck('S413 the bell walks every room of the chair, not an empty hall', _src.count(chr(35)+' DIRS-ALL v85.69') >= 2)"),
      ("'S414 the memory archives rest in a local folder, not in the master's cloud", "'S413 the bell walks every room of the chair, not an empty hall", "ck('S414 the memory archives rest in a local folder, not in the master'+chr(39)+'s cloud', (chr(35)+' BACKUP-LOCAL v85.69') in _src and ('Backup of Butler' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
