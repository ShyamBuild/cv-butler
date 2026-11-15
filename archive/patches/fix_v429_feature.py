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
if wt is not None and 'NO-SILENT-EXIT v85.51' not in '\n'.join(g):
    g[wt:wt] = ["import faulthandler as _fh; _fh.enable()  # HARD-CRASH-VOICE v85.51: if the interpreter itself dies, the stack speaks to the terminal instead of vanishing",
                "import atexit as _ax, sys as _sysx, traceback as _tbx",
                "def _name_exit():  # NO-SILENT-EXIT v85.51: every process ending rings one bell, so a bare shell prompt is never the only evidence of an ending",
                "    print('👋 chat process ended - if you did not press ^C or quit, the lines above name the cause')",
                "_ax.register(_name_exit)",
                "def _hook(_t, _v, _tb):  # HARD-CRASH-VOICE v85.51 companion: an exception that escapes every armor names its kind and message on the way out",
                "    _tbx.print_exception(_t, _v, _tb)",
                "    print('👋 chat closed by uncaught %s: %s' % (_t.__name__, _v))",
                "_sysx.excepthook = _hook",
                ""]
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
print('🔎 bells beside the loop:')
L = open('briefing.py').read().split('\n')
for k, l in enumerate(L):
    if 'HARD-CRASH-VOICE v85.51:' in l:
        for j in range(k, min(k+11, len(L))):
            print('   |', L[j].rstrip()[:140])
        break
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.51' not in t:
        open(AR, 'a').write('v85.51: NO-SILENT-EXIT installed beside the REPL loop at column zero (atexit bell on every ending, excepthook naming uncaught escapes, faulthandler voicing interpreter deaths) - no indentation surgery, no divorced partners; a bare shell prompt is never the only evidence again (S392)\n')
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
