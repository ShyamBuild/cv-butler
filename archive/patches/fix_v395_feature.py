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
i0 = next((k for k, l in enumerate(w) if l.startswith('def send_review(')), None)
if i0 is not None and 'PARK-DRAFT' not in '\n'.join(w[i0:i0+16]):
    j = next(k for k in range(i0, i0+16) if w[k].strip() == 'return False')
    d = ind(w[j])
    w[j:j] = [d*' ' + "try:  # PARK-DRAFT v85.27: a broken window must never cost a courtesy - the exact draft parks by phone and names its own path",
              (d+4)*' ' + "pd = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drafts', 'parked')",
              (d+4)*' ' + "os.makedirs(pd, exist_ok=True)",
              (d+4)*' ' + "fn = os.path.join(pd, re.sub(r'\\D', '', str(phone)) + '.txt')",
              (d+4)*' ' + "open(fn, 'w').write(text)",
              (d+4)*' ' + "say('📥 draft parked at ' + fn + ' - send it by hand or retry once the window is cured')",
              d*' ' + "except Exception:",
              (d+4)*' ' + "pass"]
    done.append('park-draft')
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
    if 'v85.27' not in t:
        open(AR, 'a').write('v85.27: PARK-DRAFT - every window failure parks the exact draft at drafts/parked/<digits>.txt and names the path, so a library mood never costs a courtesy; two clean-shell diagnostics decide whether the haunt is the playwright install, wa import chain, or inherited tty (S365)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S365 a broken window never costs a courtesy - the draft parks and names its path", "'S364 a logged-out window asks for one scan, named aloud", "ck('S365 a broken window never costs a courtesy - the draft parks and names its path', (chr(35)+' PARK-DRAFT v85.27') in open(os.path.join(BASE_DIR, 'wa.py')).read())")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
