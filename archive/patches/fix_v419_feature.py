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
snapw = list(w)
bad = next((k for k, l in enumerate(w) if 'os.path.abspath(__file__, timeout=240)' in l), None)
if bad is not None:
    w[bad] = w[bad].replace('os.path.abspath(__file__, timeout=240)))', 'os.path.abspath(__file__)), timeout=240)')
    done.append('timeout-home')
srcw = '\n'.join(w)
if srcw != W0:
    ast.parse(srcw); open('wa.py', 'w').write(srcw)
G0 = open('briefing.py').read()
g = G0.split('\n')
snapg = list(g)
if 'def _armor(' not in '\n'.join(g):
    a0 = next(k for k, l in enumerate(g) if l.startswith('def _say('))
    g[a0:a0] = ["def _armor(f):  # CHAT-ARMOR v85.43: a stumbling command confesses and the chat stays open - the master never restarts an evening for a traceback; Ctrl-C remains a choice, the only door out",
                "    def _w(*a, **k):",
                "        try:",
                "            return f(*a, **k)",
                "        except KeyboardInterrupt:",
                "            raise",
                "        except Exception as e:",
                "            print('⚠️ the house stumbled: %r - the chat stays open; nothing half-done is hidden' % (e,))",
                "            return None",
                "    return _w",
                ""]
    done.append('armor-def')
n = 0
for k, l in enumerate(g):
    if l.startswith('def do_') and (k == 0 or not g[k-1].strip().startswith('@_armor')):
        g.insert(k, '@_armor')
        n += 1
if n: done.append('armor-doors-x%d' % n)
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
print('🔎 armored doors:')
for k, l in enumerate(open('briefing.py').read().split('\n')):
    if l.strip() == '@_armor':
        print('   |', g and open('briefing.py').read().split('\n')[k+1].strip()[:80])
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.43' not in t:
        open(AR, 'a').write('v85.43: the hang-ceiling timeout returned to its own call (a blind replace had parked it inside abspath); CHAT-ARMOR wraps every do_* door so any exception confesses in one flush line and the prompt returns - Ctrl-C alone closes the chat (S383)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S383 a stumbling command confesses and the chat stays open", "'S382 the tray belongs to its desk", "ck('S383 a stumbling command confesses and the chat stays open', (chr(35)+' CHAT-ARMOR v85.43') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and open(os.path.join(BASE_DIR, 'briefing.py')).read().count('@_armor') >= 2)")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
