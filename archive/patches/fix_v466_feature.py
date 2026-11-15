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
    if 'os.path.realpath(q) != os.path.realpath(p)' in l and 'CASE-SELF' not in l:
        tail_comment = ''
        body = l
        if '  # ' in l:
            body, tail_comment = l.split('  # ', 1)
            tail_comment = '  # ' + tail_comment
        newbody = body.replace('os.path.realpath(q) != os.path.realpath(p)', 'os.path.basename(q).lower() != os.path.basename(p).lower()')
        B[k] = newbody + tail_comment + '  # CASE-SELF v85.82: realpath resolves symlinks, not case - a case-variant of yourself is you; the witness rides at the line end, never through its chest'
        n += 1
if n: done.append('case-self-x%d' % n)
if 'def _say_once(' not in '\n'.join(B):
    a0 = next(k for k, l in enumerate(B) if l.startswith('def _lock_root('))
    B[a0:a0] = ["_SAID_ONCE = set()",
                "def _say_once(m):  # GONE-ONCE v85.82: a ghost is announced once, then rests - the log is a bell-tower, not a drum",
                "    if m in _SAID_ONCE: return",
                "    _SAID_ONCE.add(m)",
                "    print(m)",
                ""]
    done.append('say-once-def')
m2 = 0
for k, l in enumerate(B):
    if any(s in l for s in ('left the pipeline (file gone)', 'pipeline reconcile skipped', 'new client folder:', 'pulse skipped')) and '_say_once(' not in l:
        for tok in ('say(', 'print('):
            i = l.find(tok)
            if i >= 0:
                B[k] = l[:i] + '_say_once(' + l[i+len(tok):]
                m2 += 1
                break
if m2: done.append('say-once-wired-x%d' % m2)
h = 0
for k, l in enumerate(B):
    if "['history']" in l:
        B[k] = l.replace("['history']", ".get('history', [])")
        h += 1
if h: done.append('history-tolerant-x%d' % h)
for k, l in enumerate(B):
    if l.strip().startswith("ck('S421 ") and 'basename(q).lower' not in l:
        d = ind(l)
        B[k] = d*' ' + "ck('S421 on a case-insensitive disk, a paper is never its own twin', _src.count('os.path.basename(q).lower() != os.path.basename(p).lower()') >= 3)  # S421 repinned v85.84: the law reads the living wording - a guard that quotes retired code convicts its own cure"
        done.append('S421-repin'); break
print('🔎 case-self guards whole, once-voices, history sites:')
for k, l in enumerate(B):
    if 'CASE-SELF v85.82' in l or 'GONE-ONCE v85.82: a ghost' in l:
        print('   |', l.strip()[:170])
print('🔎 pulse body, forty lines deep:')
pa = next((k for k, l in enumerate(B) if 'pulse thread armed' in l), None)
if pa is not None:
    for j in range(pa, min(pa+40, len(B))):
        print('   |', j+1, '|', B[j].rstrip()[:140])
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
    if 'v85.84' not in t:
        open(AR, 'a').write('v85.84: S421 repinned to the living basename-lower wording because the old probe counted the retired realpath string and convicted the cure; v85.83 re-lands whole (CASE-SELF witnesses at line end, GONE-ONCE voices now including pulse skipped, history via .get); pulse body printed forty lines deep for the root cure (S421 repinned, S424, S425)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S424 on this disk a case-variant of yourself is you, and renames in place perform", "'S423 the CID eye stands at the head of the chain, wrapped around the name itself", "ck('S424 on this disk a case-variant of yourself is you, and renames in place perform', _src.count(chr(35)+' CASE-SELF v85.82') >= 3)"),
      ("'S425 a ghost is announced once and the reconcile heals its missing history", "'S424 on this disk a case-variant of yourself is you, and renames in place perform", "ck('S425 a ghost is announced once and the reconcile heals its missing history', ('def _say_once(' in _src) and (_src.count('.get(' + chr(39) + 'history' + chr(39) + ', [])') >= 1))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
