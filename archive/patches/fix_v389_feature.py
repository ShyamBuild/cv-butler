import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
B0 = open('butler.py').read()
G0 = open('briefing.py').read()
W0 = open('wa.py').read()
M0 = set(markers(B0.split('\n'))) | set(markers(G0.split('\n'))) | set(markers(W0.split('\n')))
def crlf(lines, a, b, tag):
    n = 0
    for k in range(a, b):
        l = lines[k]
        nl = l.replace(".write(c + '\\n')", ".write(c + '\\r\\n')").replace(".write(k + '\\n')", ".write(k + '\\r\\n')").replace(".write('^C\\n')", ".write('^C\\r\\n')").replace(".write('\\n')", ".write('\\r\\n')")
        if nl != l:
            if tag not in nl:
                nl = nl.rstrip() + '  # ' + tag + ': in raw mode the writer is the driver - LF alone leaves the column where it stood'
            lines[k] = nl; n += 1
    return n
B = B0.split('\n')
snap = list(B)
m0 = next(k for k, l in enumerate(B) if l.startswith('def menu_key('))
m1 = next(k for k in range(m0 + 1, len(B)) if B[k].startswith('def '))
n = crlf(B, m0, m1, 'CRLF-RAW v85.22')
if n: done.append('crlf-butler-x%d' % n)
if 'def _vision_safe(' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.startswith('def seat_rename_check('))
    B[i:i] = ["_IN_CEREMONY = [False]",
              "def _vision_safe(p):  # VISION-THREAD v85.22: the vision eye reads in its own thread, so whatever loop it borrows lives and dies in its own room and never lies across the thumb's path",
              "    import threading",
              "    out = []",
              "    def _w():",
              "        try:",
              "            out.append(get_visual_name(p))",
              "        except Exception:",
              "            out.append('')",
              "    th = threading.Thread(target=_w, daemon=True)",
              "    th.start(); th.join(45)",
              "    return out[0] if out else ''",
              ""]
    done.append('vision-thread')
s0 = next(k for k, l in enumerate(B) if l.startswith('def seat_rename_check('))
s1 = next(k for k in range(s0 + 1, len(B)) if B[k].startswith('def '))
for k in range(s0, s1):
    if 'get_visual_name(p)' in B[k] and '_vision_safe' not in B[k]:
        B[k] = B[k].replace('get_visual_name(p)', '_vision_safe(p)')
        done.append('vision-used'); break
for k in range(s0, s1):
    if B[k].strip().startswith('whole = (only is None)'):
        d = ind(B[k])
        B[k+1:k+1] = [d*' ' + "if whole and _IN_CEREMONY[0]: return 0  # ONCE-PER-COMMAND v85.22: up's self-refresh re-enters up_cmd; the whole-chair pass runs once per keystroke, and each miss confesses once",
                      d*' ' + "if whole: _IN_CEREMONY[0] = True"]
        done.append('ceremony-once'); break
for k in range(s0, s1):
    if B[k].strip().startswith('return n') and '_IN_CEREMONY[0] = False' not in '\n'.join(B[k-3:k]):
        d = ind(B[k])
        B.insert(k, d*' ' + "if whole: _IN_CEREMONY[0] = False")
        done.append('ceremony-release'); break
for k in range(s0, s1):
    if B[k].strip().startswith("t = extract_text(p) or ''") and B[k-2].strip().startswith('def _name_from_first_line') is False and 'extract_text_ocr' not in '\n'.join(B[s0-20:s1]):
        pass
f0 = next((k for k, l in enumerate(B) if l.startswith('def _name_from_first_line(')), None)
if f0 is not None and 'extract_text_ocr' not in '\n'.join(B[f0:f0+16]):
    for k in range(f0, f0+6):
        if B[k].strip().startswith("t = extract_text(p) or ''"):
            d = ind(B[k])
            B[k:k+1] = [d*' ' + "t = extract_text(p) or ''",
                        d*' ' + "if not t.strip():",
                        (d+4)*' ' + "try: t = extract_text_ocr(p) or ''  # FIRST-LINE v85.20 (ocr-fallback v85.22): a text layer that refuses to open yields to the capped pixels",
                        (d+4)*' ' + "except Exception: t = ''"]
            done.append('firstline-ocr'); break
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
g = G0.split('\n')
snapg = list(g)
si = next((k for k, l in enumerate(g) if l.startswith('def _smart_input(')), None)
if si is not None:
    sj = next(k for k in range(si + 1, len(g)) if g[k].startswith('def '))
    n = crlf(g, si, sj, 'CRLF-RAW v85.22')
    if n: done.append('crlf-briefing-x%d' % n)
srcg = '\n'.join(g)
if srcg != G0:
    ast.parse(srcg); open('briefing.py', 'w').write(srcg)
w = W0.split('\n')
snapw = list(w)
ki = next((k for k, l in enumerate(w) if l.startswith('def _key(')), None)
if ki is not None:
    kj = next(k for k in range(ki + 1, len(w)) if w[k].startswith('def '))
    n = crlf(w, ki, kj, 'CRLF-RAW v85.22')
    if n:
        done.append('crlf-wa-x%d' % n)
        srcw = '\n'.join(w)
        ast.parse(srcw); open('wa.py', 'w').write(srcw)
M1 = set(markers(open('butler.py').read().split('\n'))) | set(markers(open('briefing.py').read().split('\n'))) | set(markers(open('wa.py').read().split('\n')))
lost = M0 - M1
if lost:
    print('⛔ witness diff:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff: 0 laws lost -', len(M0), 'before,', len(M1), 'after')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.22' not in t:
        open(AR, 'a').write('v85.22: CRLF-RAW in every raw-mode writer (in raw mode the writer is the driver - LF alone leaves the column where it stood; this was the ghost space since v84.45); VISION-THREAD isolates the vision eye loop from playwright; ONCE-PER-COMMAND stops the self-refresh double ceremony; FIRST-LINE gains an OCR fallback (S358, S359, S360)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
_br = open('briefing.py').read()
_wa = open('wa.py').read()
def anch(*needles):
    for n2 in needles:
        hit = [k for k, l in enumerate(B) if n2 in l]
        if hit: return hit[-1]
    return None
GU = [("'S358 in raw mode the writer is the driver - every raw newline carries its carriage", "'S357 no idle loop may lie across the thumb's path", "ck('S358 in raw mode the writer is the driver - every raw newline carries its carriage', (chr(35)+' CRLF-RAW v85.22') in _src and (chr(35)+' CRLF-RAW v85.22') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and (chr(35)+' CRLF-RAW v85.22') in open(os.path.join(BASE_DIR, 'wa.py')).read())"),
      ("'S359 the vision eye reads in its own thread and never lends the thumb its loop", "'S358 in raw mode the writer is the driver - every raw newline carries its carriage", "ck('S359 the vision eye reads in its own thread and never lends the thumb its loop', (chr(35)+' VISION-THREAD v85.22') in _src and ('_vision_safe(p)' in _src))"),
      ("'S360 the whole-chair ceremony runs once per keystroke and each miss confesses once", "'S359 the vision eye reads in its own thread and never lends the thumb its loop", "ck('S360 the whole-chair ceremony runs once per keystroke and each miss confesses once', (chr(35)+' ONCE-PER-COMMAND v85.22') in _src and ('_IN_CEREMONY' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
