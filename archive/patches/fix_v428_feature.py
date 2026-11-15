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
G0 = open('briefing.py').read()
g = G0.split('\n')
snapg = list(g)
wt = None
for k in range(len(g) - 1, -1, -1):
    if g[k].strip() == 'while True:':
        wt = k; break
if wt is not None and 'NO-SILENT-EXIT' not in '\n'.join(g[wt:]):
    d = ind(g[wt])
    g.insert(wt, d*' ' + "import faulthandler; faulthandler.enable()  # HARD-CRASH-VOICE v85.51: if the interpreter itself dies, the stack speaks to the terminal instead of vanishing")
    wt += 1
    body = g[wt:]
    g[wt:] = [d*' ' + "try:"] + [(l if l.strip() == '' else ('    ' + l)) for l in body] + [
        d*' ' + "except SystemExit as _se:  # NO-SILENT-EXIT v85.51: every exit names itself - a master must never find a bare shell prompt and wonder whether the house left or fell",
        d*' ' + "    print('👋 chat closed by SystemExit: %r' % (_se.code,))",
        d*' ' + "except BaseException as _be:",
        d*' ' + "    print('👋 chat closed by %r - every exit names itself' % (_be,))"]
    done.append('no-silent-exit')
srcg = '\n'.join(g)
if srcg != G0:
    ast.parse(srcg); open('briefing.py', 'w').write(srcg)
M1 = perfile()
lost = set()
for fn in M0:
    lost |= (M0[fn] - M1.get(fn, set()))
if lost:
    print('⛔ witness diff per file:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff per file: 0 laws lost')
print('🔎 repl tail now:')
L = open('briefing.py').read().split('\n')
for k, l in enumerate(L):
    if 'HARD-CRASH-VOICE v85.51' in l:
        for j in range(k, min(k+6, len(L))):
            print('   |', L[j].rstrip()[:140])
        for j in range(max(0, len(L)-6), len(L)):
            print('   |', L[j].rstrip()[:140])
        break
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.51' not in t:
        open(AR, 'a').write('v85.51: NO-SILENT-EXIT wraps the REPL tail so SystemExit and any BaseException print a named goodbye, and HARD-CRASH-VOICE enables faulthandler so interpreter-level deaths leave their stack - a bare shell prompt must never be the only evidence of an ending (S392)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S392 every exit names itself - a bare shell prompt is never the only evidence", "'S391 the picked paper's own eyes stand before any shared store", "ck('S392 every exit names itself - a bare shell prompt is never the only evidence', (chr(35)+' NO-SILENT-EXIT v85.51') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and (chr(35)+' HARD-CRASH-VOICE v85.51') in open(os.path.join(BASE_DIR, 'briefing.py')).read())")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
