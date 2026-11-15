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
if 'def _lock_root(' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.startswith('def _event_tick('))
    B[i:i] = ["def _lock_root():  # LOCK-ROOT v85.54: when a verb is called from a folder that is not a desk, the live lock names the desk the house is actually serving",
              "    try:",
              "        for fn in os.listdir(BASE_DIR):",
              "            if fn.startswith('butler_') and fn.endswith('.lock'):",
              "                txt = open(os.path.join(BASE_DIR, fn)).read().strip()",
              "                if '|' in txt:",
              "                    p = txt.split('|', 1)[1]",
              "                    if os.path.isdir(p): return p",
              "    except Exception:",
              "        pass",
              "    return ''",
              ""]
    done.append('lock-root-def')
ek = next((k for k, l in enumerate(B) if 'folder does not exist' in l), None)
if ek is not None and 'LOCK-ROOT v85.54: the lock is' not in '\n'.join(B[max(0,ek-4):ek]):
    j = ek - 1
    while j > 0 and not B[j].strip().startswith('if '):
        j -= 1
    d = ind(B[j])
    B.insert(j, d*' ' + "root = _lock_root() or root  # LOCK-ROOT v85.54: the lock is the house's address book - a verb called from the workshop serves the living desk instead of refusing")
    done.append('lock-root-wire')
    print('🔎 lock-root wired above the folder check:')
    for k2 in range(j, min(j+4, len(B))):
        print('   |', B[k2].rstrip()[:150])
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
    if 'v85.54' not in t:
        open(AR, 'a').write('v85.54: LOCK-ROOT - verbs called from a non-desk folder resolve the live lock desk instead of printing folder-does-not-exist; the bell-tower remains the butler log, where converted and watch-renamed lines live (S396)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S396 a verb called from anywhere serves the living desk", "'S395 the doorbell owns its heartbeat and one process alone may ring it", "ck('S396 a verb called from anywhere serves the living desk', ('def _lock_root(' in _src) and ('root = _lock_root() or root' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
