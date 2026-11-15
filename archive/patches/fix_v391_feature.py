import ast, os, re
done = []
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
W0 = open('wa.py').read()
M0 = set(markers(W0.split('\n')))
w = W0.split('\n')
snap = list(w)
s0 = next((k for k, l in enumerate(w) if l.startswith('def send_review(')), None)
if s0 is not None and 'PLAYWRIGHT-PROCESS' not in '\n'.join(w[s0:s0+20]):
    s1 = next(k for k in range(s0 + 1, len(w)) if w[k].startswith('def ') or (w[k].strip() and not w[k].startswith(' ') and not w[k].startswith('#') and not w[k].startswith(')') and not w[k].startswith('th.') and not w[k].startswith('box') and not w[k].startswith('r =') and not w[k].startswith('if isinstance') and not w[k].startswith('return r') and not w[k].startswith('import threading') and not w[k].startswith('def _w'))
    w[s0:s1] = ["def send_review(phone, text, say=print, *a, **k):  # PLAYWRIGHT-PROCESS v85.24: a brand-new process has no event loops at all - the ritual inherits the tty so the master's bare keys still answer, and the exit code carries the truth home",
                "    import subprocess, sys",
                "    code = 'import sys, wa; sys.exit(0 if wa._send_review_body(%r, %r, print) else 1)' % (phone, text)",
                "    r = subprocess.call([sys.executable, '-c', code], cwd=os.path.dirname(os.path.abspath(__file__)))",
                "    if r != 0:",
                "        say('⚠️ whatsapp failed in its own process - the draft rests in the field of the log; retry with: python3 -c \"import wa; wa._send_review_body(%s, %s, print)\"' % (repr(phone), repr(text)))",
                "        return False",
                "    return True"]
    done.append('playwright-process')
srcw = '\n'.join(w)
if srcw != W0:
    ast.parse(srcw); open('wa.py', 'w').write(srcw)
M1 = set(markers(open('wa.py').read().split('\n')))
lost = M0 - M1
if lost:
    print('⛔ witness diff:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff: 0 laws lost -', len(M0), 'before,', len(M1), 'after')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.24' not in t:
        open(AR, 'a').write('v85.24: PLAYWRIGHT-PROCESS - thread isolation outrun by whatever loop haunts this process; the window ritual now runs in a brand-new python process with the tty inherited and the exit code as its report; a probe recipe lives in the ledger for any future failure (S362)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S362 the window ritual lives in its own process where no loop can exist", "'S361 the window ritual lives in its own thread and no loop may reach it", "ck('S362 the window ritual lives in its own process where no loop can exist', (chr(35)+' PLAYWRIGHT-PROCESS v85.24') in open(os.path.join(BASE_DIR, 'wa.py')).read() and ('subprocess.call' in open(os.path.join(BASE_DIR, 'wa.py')).read()))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
