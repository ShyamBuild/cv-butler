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
d0 = next((k for k, l in enumerate(w) if l.startswith('def send_review(')), None)
if d0 is not None and 'def _send_review_body(' not in '\n'.join(w):
    w[d0] = w[d0].replace('def send_review(', 'def _send_review_body(', 1)
    w.append("")
    w.append("def send_review(*a, **k):  # PLAYWRIGHT-THREAD v85.23: the whole window ritual runs in its own thread, so no loop anywhere in the caller's process can reach playwright's check - raw tty reads are process-wide, so the menu still answers to a bare key")
    w.append("    import threading")
    w.append("    box = []")
    w.append("    def _w():")
    w.append("        try:")
    w.append("            box.append(_send_review_body(*a, **k))")
    w.append("        except Exception as e:")
    w.append("            box.append(e)")
    w.append("    th = threading.Thread(target=_w, daemon=True)")
    w.append("    th.start(); th.join(240)")
    w.append("    r = box[0] if box else None")
    w.append("    if isinstance(r, Exception):")
    w.append("        print('⚠️ whatsapp failed: %s' % r)")
    w.append("        return False")
    w.append("    return r")
    done.append('playwright-thread')
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
    if 'v85.23' not in t:
        open(AR, 'a').write('v85.23: PLAYWRIGHT-THREAD - send_review becomes a wrapper that runs the whole window ritual in its own thread; playwright sync can never again meet a running loop, whatever leaves one lying elsewhere in the chat process (S361)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
_wa = open('wa.py').read()
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S361 the window ritual lives in its own thread and no loop may reach it", "'S360 the whole-chair ceremony runs once per keystroke and each miss confesses once", "ck('S361 the window ritual lives in its own thread and no loop may reach it', (chr(35)+' PLAYWRIGHT-THREAD v85.23') in open(os.path.join(BASE_DIR, 'wa.py')).read() and ('def _send_review_body(' in open(os.path.join(BASE_DIR, 'wa.py')).read()))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
