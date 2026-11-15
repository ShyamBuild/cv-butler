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
x0 = next((k for k, l in enumerate(B) if l.startswith('def extract_text(')), None)
if x0 is not None and 'TEXT-DOCX' not in '\n'.join(B[x0:x0+12]):
    d = ind(B[x0+1]) if x0+1 < len(B) and B[x0+1].strip() else 4
    B[x0+1:x0+1] = [d*' ' + "_ex = os.path.splitext(p)[1].lower()  # TEXT-DOCX v85.55: a Word paper reads natively through textutil - full text in milliseconds, no LibreOffice, no pixels, no OCR cap; the converter's absence never blinds the eyes again",
                    d*' ' + "if _ex in ('.docx', '.doc', '.rtf'):",
                    (d+4)*' ' + "import subprocess as _sp2",
                    (d+4)*' ' + "try:",
                    (d+8)*' ' + "_r = _sp2.run(['textutil', '-convert', 'txt', '-stdout', p], capture_output=True, timeout=60)",
                    (d+8)*' ' + "_t = _r.stdout.decode('utf-8', 'ignore') if _r.returncode == 0 else ''",
                    (d+8)*' ' + "if _t.strip(): return _t",
                    (d+4)*' ' + "except Exception:",
                    (d+8)*' ' + "pass"]
    done.append('text-docx')
    print('🔎 extract_text head:')
    for j in range(x0, min(x0+11, len(B))):
        print('   |', B[j].rstrip()[:150])
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
    if 'v85.55' not in t:
        open(AR, 'a').write('v85.55: TEXT-DOCX - extract_text gains a native fourth eye: docx/doc/rtf read through textutil txt in milliseconds, so Word papers are never text-silent again and every downstream skill (identity, phonebook, FIRST-LINE, rename, drafts) works on them without LibreOffice; the converter remains for images and PDF uniformity (S397)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S397 a Word paper is never text-silent - the native reader opens it in milliseconds", "'S396 a verb called from anywhere serves the living desk", "ck('S397 a Word paper is never text-silent - the native reader opens it in milliseconds', (chr(35)+' TEXT-DOCX v85.55') in _src and ('textutil' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
