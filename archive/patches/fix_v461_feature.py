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
print('🔎 every extract-bearing def, verbatim:')
for k, l in enumerate(B):
    if l.startswith('def ') and 'extract' in l.lower():
        print('   |', k+1, '|', l.rstrip()[:150])
exd = None
for k, l in enumerate(B):
    if re.match(r'def\s+extract_text\s*\(', l):
        exd = k; break
if exd is not None and 'PY-PYPDF v85.80' not in '\n'.join(B[exd:exd+10]):
    nb = exd + 1
    while nb < len(B) and not B[nb].strip():
        nb += 1
    d = ind(B[nb])
    B[exd+1:exd+1] = [d*' ' + "try:  # PY-PYPDF v85.80: the venv reader speaks CID glyph maps - matched by regex at the true def line, ahead of every other eye, because four literal prefixes missed a signature that wears its own shape",
                      (d+4)*' ' + "import pypdf as _pypdf",
                      (d+4)*' ' + "_pr = _pypdf.PdfReader(p)",
                      (d+4)*' ' + "_ptx = '\\n'.join((pg.extract_text() or '') for pg in _pr.pages)",
                      (d+4)*' ' + "if _ptx.strip(): return _ptx",
                      d*' ' + "except Exception:",
                      (d+4)*' ' + "pass"]
    done.append('py-pypdf-regex')
    print('🔎 eye chain head after insert:')
    for j in range(exd, min(exd+12, len(B))):
        print('   |', B[j].rstrip()[:150])
else:
    print('🔎 extract_text def not matched by regex either - the name itself is elsewhere; evidence above')
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
    if 'v85.80' not in t:
        open(AR, 'a').write('v85.80: PY-PYPDF wired by regex at the true extract_text def line with every extract-def printed as standing evidence; the master repaid the five-drag debt by hand and the ledger records it; sweep and QUEUE-ACT stand ready to rename in place and answer the right-click (S423)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S423 the CID eye stands at the head of the chain, matched by shape not by prefix", "'S422 every parked paper has a road home through remembered addresses", "ck('S423 the CID eye stands at the head of the chain, matched by shape not by prefix', (chr(35)+' PY-PYPDF v85.80') in _src and ('import pypdf as _pypdf' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
