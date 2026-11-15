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
W0 = open('wa.py').read()
w = W0.split('\n')
snap = list(w)
c0 = next(k for k, l in enumerate(w) if l.startswith('def _ctx('))
if 'def _pw(' not in '\n'.join(w):
    w[c0:c0] = ["_PW = [None]",
                "def _pw():  # ONE-START v85.30: playwright is started once per process and shared by every door - the ladder proved a second sync start is the library's forbidden door, and its complaint about asyncio was a lie about arity",
                "    if _PW[0] is None:",
                "        from playwright.sync_api import sync_playwright",
                "        _PW[0] = sync_playwright().start()",
                "    return _PW[0]",
                ""]
    done.append('one-start-def')
n = 0
for k, l in enumerate(w):
    if 'sync_playwright().start()' in l and 'def _pw(' not in '\n'.join(w[max(0,k-8):k]) and '_PW[0] = sync_playwright().start()' not in l:
        w[k] = l.replace('sync_playwright().start()', '_pw()')
        n += 1
if n: done.append('one-start-use-x%d' % n)
srcw = '\n'.join(w)
if srcw != W0:
    ast.parse(srcw); open('wa.py', 'w').write(srcw)
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
    if 'v85.30' not in t:
        open(AR, 'a').write('v85.30: ONE-START - the ladder named the ghost: door 1 start ok, door 2 cdp ECONNREFUSED (warm client down), fallback _ctx started playwright a SECOND time and the library refused with its asyncio lie; a module singleton _pw() starts once and shares; S368 pins exactly one start call in wa (S368)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S368 playwright is started once per process and shared by every door", "'S367 no shadow may stand between playwright and its own heartbeat", "ck('S368 playwright is started once per process and shared by every door', open(os.path.join(BASE_DIR, 'wa.py')).read().count('sync_playwright().start()') == 1 and ('def _pw(' in open(os.path.join(BASE_DIR, 'wa.py')).read()))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
