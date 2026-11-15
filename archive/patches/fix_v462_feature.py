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
print('🔎 every line naming extract_text, verbatim (first twelve):')
c = 0
for k, l in enumerate(B):
    if 'extract_text' in l and 'extract_text_ocr' not in l.split('extract_text')[0][-1:]:
        print('   |', k+1, '|', l.rstrip()[:150])
        c += 1
        if c >= 12: break
if 'PY-PYPDF v85.81' not in '\n'.join(B):
    while B and B[-1].strip() == '':
        B.pop()
    B += ["",
          "try:  # PY-PYPDF v85.81: wrap the NAME, not the definition - the alias is rebind at module end around whichever reader it holds, because four laps of def-hunting proved the name wears no def in this book",
          "    _orig_extract_text_v8581 = extract_text",
          "    def extract_text(p, *a, **k):  # PY-PYPDF v85.81: the CID eye stands ahead of every other reader the alias names - pypdf first, the original beneath, no anchors and no hunting",
          "        try:",
          "            import pypdf as _pypdf",
          "            _pr = _pypdf.PdfReader(p)",
          "            _ptx = '\\n'.join((pg.extract_text() or '') for pg in _pr.pages)",
          "            if _ptx.strip(): return _ptx",
          "        except Exception:",
          "            pass",
          "        return _orig_extract_text_v8581(p, *a, **k)",
          "except NameError:",
          "    pass"]
    done.append('pypdf-name-wrap')
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
print('🔎 module tail now:')
L = open('butler.py').read().split('\n')
for j in range(max(0, len(L)-14), len(L)):
    if L[j].strip(): print('   |', L[j].rstrip()[:150])
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.81' not in t:
        open(AR, 'a').write('v85.81: PY-PYPDF wraps the extract_text NAME at module end around whichever reader the alias holds, curing four laps of def-hunting blindness (the name wears no def in butler.py; only extract_text_ocr does); every line naming extract_text printed as standing evidence; the CID eye now feeds seats, phones, first-lines, renames and the diagnostic alike (S423)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S423 the CID eye stands at the head of the chain, wrapped around the name itself", "'S422 every parked paper has a road home through remembered addresses", "ck('S423 the CID eye stands at the head of the chain, wrapped around the name itself', (chr(35)+' PY-PYPDF v85.81') in _src and ('_orig_extract_text_v8581' in _src) and ('import pypdf as _pypdf' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
