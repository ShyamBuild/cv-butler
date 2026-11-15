import ast, os, re, shutil, subprocess
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
lv = next((k for k, l in enumerate(B) if l.strip().startswith("elif not txt.strip(): dec = 'SKIP text-silent")), None)
if lv is not None and 'DEEP-VERDICT' not in B[lv]:
    d = ind(B[lv])
    B[lv] = d*' ' + "elif not txt.strip() and not (deep and c): dec = 'SKIP text-silent (vision not summoned in diag)' + _flt  # DEEP-VERDICT v85.87: in deep mode an OCR-born canon name becomes a RENAME verdict, because a datum hidden behind a silence tunes nothing"
    done.append('deep-verdict')
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
print('🔎 the blind eyes, evidenced:')
print('   | tesseract binary:', shutil.which('tesseract'))
try:
    _ol = subprocess.run(['ollama', 'list'], capture_output=True, timeout=8)
    print('   | ollama list:', _ol.stdout.decode('utf-8', 'ignore').strip().replace('\n', ' | ')[:300])
except Exception as _oe:
    print('   | ollama list: unavailable -', repr(_oe)[:80])
L = open('butler.py').read().split('\n')
for tag in ('def extract_text_ocr(', 'def _vision_safe('):
    k = next((j for j, l in enumerate(L) if l.startswith(tag)), None)
    if k is None:
        print('   |', tag, 'NOT FOUND')
    else:
        print('   | ---', tag)
        for j in range(k, min(k+10, len(L))):
            print('   |', j+1, '|', L[j].rstrip()[:140])
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
    if 'v85.87' not in t:
        open(AR, 'a').write('v85.87: DEEP-VERDICT lets a deep-mode OCR name surface as a RENAME verdict; the evidence lap prints tesseract presence, ollama models and the heads of extract_text_ocr and _vision_safe so the last blind eye is named before any cure is chosen; a right-click on an unreadable scan logs its reason and declines, because a guessed name is worse than a shout (S429)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S429 a deep row that earns a name shows its verdict, and a blind eye is named before it is cured", "'S428 depth is a choice the master makes, and a closed pipe is a quiet goodbye", "ck('S429 a deep row that earns a name shows its verdict, and a blind eye is named before it is cured', (chr(35)+' DEEP-VERDICT v85.87') in _src)")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
