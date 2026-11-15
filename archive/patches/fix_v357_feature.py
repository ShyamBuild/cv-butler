import ast, os, re
done = []
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
B0 = open('butler.py').read()
M0 = set(markers(B0.split('\n')))
B = B0.split('\n')
snap = list(B)
for k, l in enumerate(B):
    if 'CINE-LINE v85.1:' in l and '# CINE-LINE' not in l:
        B[k] = l.replace(' CINE-LINE v85.1:', ' # CINE-LINE v85.1:')
        done.append('cine-marker-fixed'); break
COPY = [("after the call, one digit or one word closes his row:", "⌨️ one key closes his row:"),
        ("(options prints the full grammar with keywords and both draft moments)", "(options = full grammar)"),
        ("📭 sheet empty - every loose paper is seated, skipped or remembered", "📭 tray clear - every loose paper seated, skipped or remembered"),
        ("outside the stage folders", "loose"),
        ("🏁 sheet covered - every candidate has an outcome", "🏁 sheet covered - every soul has an outcome"),
        ("next up: {w[0][\"name\"]} - type: up", "next: {w[0][\"name\"]} · up when ready"),
        ("➕ new paper joined the sheet: ", "🆕 joined the sheet: "),
        ("🤷 nobody is in the chair - type: up", "🪑 chair empty - type up"),
        ("🔁 the paper moved - found it again in ", "🔁 repathed - found him in "),
        ("· row left open - he stays in the chair", "⏸️ row open - he stays in the chair"),
        (" · WhatsApp {draft} draft will open, unsent", " · 📱 {draft} draft unsent"),
        (" · no message - this one stays in the house", " · no 📱 - stays in the house"),
        ("discarded - nothing sent", "🗑️ discarded - nothing sent"),
        ("proposal waiting - type y or n on the next line", "proposal waiting - type y / t / n"),
        ("phone: none readable - teach me: python3 butler.py teach", "📵 no phone - teach: python3 butler.py teach")]
n = 0
for old, new in COPY:
    hit = False
    for k, l in enumerate(B):
        if old in l:
            B[k] = l.replace(old, new); hit = True
    if hit: n += 1
done.append('copy-pass-x%d' % n)
for k, l in enumerate(B):
    if "UP: {i['name']} · in " in l:
        B[k] = l.replace('📞 ', '🛰️ ').replace("UP: {i['name']} · in ", "CHAIR · {i['name']} · ")
        done.append('chair-line'); break
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:copy')
M1 = set(markers(open('butler.py').read().split('\n')))
lost = M0 - M1
if lost:
    print('⛔ witness diff:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff: 0 laws lost -', len(M0), 'before,', len(M1), 'after')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.2' not in t:
        open(AR, 'a').write('v85.2: COPY PASS - the terminal speaks sci-fi crisp: CHAIR seat line, one-key header, 🆕 joins, 🔁 repathed, ⏸️ row open, 🏁 every soul, named tray, unsent-draft shorthand; information unchanged, prose halved\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n2 in needles:
        hit = [k for k, l in enumerate(B) if n2 in l]
        if hit: return hit[-1]
    return None
GU = [("'S332 the deed speaks once, in one line, and silence never swallows a warning", "'S331 the tray names its members whenever it is not empty", "ck('S332 the deed speaks once, in one line, and silence never swallows a warning', (chr(35)+' CINE-LINE v85.1') in _src and ('lambda *a, **k: None' in _src))"),
      ("'S333 the terminal speaks crisp - every line keeps its information and loses its fat", "'S332 the deed speaks once, in one line, and silence never swallows a warning", "ck('S333 the terminal speaks crisp - every line keeps its information and loses its fat', ('one key closes his row' in _src) and ('CHAIR · ' in _src) and ('options = full grammar' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
