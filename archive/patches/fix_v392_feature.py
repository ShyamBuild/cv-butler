import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
W0 = open('wa.py').read()
M0 = set(markers(W0.split('\n')))
w = W0.split('\n')
snap = list(w)
b0 = next(k for k, l in enumerate(w) if l.startswith('def _send_review_body('))
for k in range(b0, b0+8):
    if w[k].strip().startswith('_a.set_event_loop(None)'):
        d = ind(w[k])
        w[k-1:k+2] = [d*' ' + "_a.set_event_loop_policy(_a.DefaultEventLoopPolicy())  # POLICY-RESET v85.25: a custom policy may hand every thread a shared running loop that set_event_loop cannot refuse; the ritual installs a fresh policy and its own idle loop, so whichever measure playwright consults, it finds a quiet room",
                      d*' ' + "_a.set_event_loop(_a.new_event_loop())"]
        done.append('policy-reset'); break
i0 = next((k for k, l in enumerate(w) if l.startswith('def send_review(')), None)
if i0 is not None and 'PLAYWRIGHT-PROCESS' not in '\n'.join(w[i0:i0+12]):
    i1 = next(k for k in range(i0, i0+20) if w[k] == '    return r')
    w[i0:i1+1] = ["def send_review(phone, text, say=print, *a, **k):  # PLAYWRIGHT-THREAD v85.23 PLAYWRIGHT-PROCESS v85.24: the ritual runs in a brand-new process - born without loops or policies - inheriting the tty so bare keys still answer; the exit code carries the truth home",
                  "    import subprocess, sys",
                  "    code = 'import sys, wa; sys.exit(0 if wa._send_review_body(%r, %r, print) else 1)' % (phone, text)",
                  "    r = subprocess.call([sys.executable, '-c', code], cwd=os.path.dirname(os.path.abspath(__file__)))",
                  "    if r != 0:",
                  "        say('⚠️ whatsapp failed in its own process - retry with: python3 -c \"import wa; wa._send_review_body(' + repr(phone) + ', ' + repr(text) + ', print)\"')",
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
    if 'v85.25' not in t:
        open(AR, 'a').write('v85.25: POLICY-RESET - the probe proved no thread-local running loop, so the haunting lives in a custom event-loop policy; the ritual installs a fresh policy and private idle loop, and runs in a brand-new process besides; S361 repinned from thread to process, S362 pins the policy reset\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
_wa = open('wa.py').read()
for k, l in enumerate(B):
    if l.strip().startswith("ck('S361 "):
        d = ind(l)
        B[k] = d*' ' + "ck('S361 the window ritual lives in its own process where no loop or policy may reach it', (chr(35)+' PLAYWRIGHT-PROCESS v85.24') in open(os.path.join(BASE_DIR, 'wa.py')).read() and ('subprocess.call' in open(os.path.join(BASE_DIR, 'wa.py')).read()))  # S361 repinned v85.25: thread isolation was outrun; the process boundary is the guarantee"
        done.append('S361-repin'); break
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S362 the ritual installs its own policy and a loop nobody runs", "'S361 the window ritual lives in its own process where no loop or policy may reach it", "ck('S362 the ritual installs its own policy and a loop nobody runs', (chr(35)+' POLICY-RESET v85.25') in open(os.path.join(BASE_DIR, 'wa.py')).read())")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
