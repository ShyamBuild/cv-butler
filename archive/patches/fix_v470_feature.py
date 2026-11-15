import ast, os, re, shutil, subprocess, time
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
o0 = next((k for k, l in enumerate(B) if l.startswith('def extract_text_ocr(')), None)
if o0 is not None and 'def ocr_probe(' not in '\n'.join(B):
    B[o0:o0] = ["def ocr_probe(p):  # OCR-PROBE v85.88: one command times the capped OCR eye on a named paper and prints what it reads - silence with a reason, speech with a head, never a guess",
                "    import time as _tm",
                "    t0 = _tm.time()",
                "    try:",
                "        t = extract_text_ocr(p) or ''",
                "    except Exception as _oe:",
                "        t = ''",
                "        print('ocr_probe error:', repr(_oe)[:120])",
                "    dt = _tm.time() - t0",
                "    print('ocr_probe: %.1fs · %d chars · %s' % (dt, len(t), p))",
                "    print('ocr_probe head:', t[:300].replace(chr(10), ' | '))",
                "    return t",
                ""]
    done.append('ocr-probe')
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
print('🔎 binaries:')
print('   | tesseract:', shutil.which('tesseract'))
print('   | pdftoppm :', shutil.which('pdftoppm'))
print('   | sips     :', shutil.which('sips'))
L = open('butler.py').read().split('\n')
o1 = next((k for k, l in enumerate(L) if l.startswith('def extract_text_ocr(')), None)
if o1 is not None:
    o2 = next((k for k in range(o1+1, len(L)) if L[k].startswith('def ')), len(L))
    print('🔎 extract_text_ocr, whole body verbatim:')
    for j in range(o1, min(o2, o1+60)):
        print('   |', j+1, '|', L[j].rstrip()[:140])
M1 = perfile()
lost = set()
for fn in M0:
    lost |= (M0[fn] - M1.get(fn, set()))
if lost:
    print('⛔ witness diff per file:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff per file: 0 laws lost')
import importlib, sys
sys.path.insert(0, os.getcwd())
try:
    import butler as _bt
    importlib.reload(_bt)
    _rp = None
    _rr = _bt._lock_root() or (_bt.desk_load() or {}).get('primary') or os.getcwd()
    for dp, dn, fn in os.walk(_rr):
        for y in fn:
            if y.lower().endswith('.pdf') and not y.lower().startswith('jd'):
                _rp = os.path.join(dp, y); break
        if _rp: break
    if _rp:
        print('🔎 live probe at ship time:')
        _bt.ocr_probe(_rp)
except Exception as _pe:
    print('🔎 live probe skipped:', repr(_pe)[:120])
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.88' not in t:
        open(AR, 'a').write('v85.88: OCR-PROBE verb times extract_text_ocr on a named paper and prints its head; tesseract 5.5.4 installed by the master; the alias hunt closed - the pypdf inserts lived inside extract_text_ocr all along and extract_text aliases it, chained by the v85.81 wrapper; the rasteriser question (pdftoppm/Quartz) stands evidenced for next lap (S430)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S430 the OCR eye can be probed by one command, timed and headed, before any cure is chosen", "'S429 a deep row that earns a name shows its verdict, and a blind eye is named before it is cured", "ck('S430 the OCR eye can be probed by one command, timed and headed, before any cure is chosen', ('def ocr_probe(' in _src) and (chr(35)+' OCR-PROBE v85.88') in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
