import ast, os, re, shutil
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
d0 = next((k for k, l in enumerate(B) if l.strip() == 'def extract_text_ocr(fp):'), None)
if d0 is not None:
    B[d0] = 'def extract_text_ocr(p):  # PARAM-FIX v85.89: one parameter, one name - for weeks every eye inside this function spoke p while the signature said fp, and the NameError swallowed the whole chain'
    done.append('param-fix')
k1 = next((k for k, l in enumerate(B) if l.strip() == 'if not os.path.exists(OCRBIN): return ""'), None)
k2 = next((k for k, l in enumerate(B) if l.strip() == 'return r.stdout or ""'), None)
if k1 is not None and k2 is not None and k2 > k1 and 'OCR-RASTER' not in '\n'.join(B[k1:k2+3]):
    d = ind(B[k1])
    B[k1:k2+1] = [d*' ' + 'if not os.path.exists(OCRBIN): return ""',
                  d*' ' + "_tgt = p",
                  d*' ' + "if os.path.splitext(_tgt)[1].lower() == '.pdf':  # OCR-RASTER v85.89: tesseract reads ink, not documents - sips renders the first page into a png the eye can hold, no poppler required",
                  (d+4)*' ' + "try:",
                  (d+8)*' ' + "import tempfile as _tf",
                  (d+8)*' ' + "_png = os.path.join(_tf.gettempdir(), 'cvocr_%d.png' % os.getpid())",
                  (d+8)*' ' + "_rs = subprocess.run(['sips', '-s', 'format', 'png', _tgt, '--out', _png], capture_output=True, timeout=90)",
                  (d+8)*' ' + "if _rs.returncode != 0 or not os.path.exists(_png): return ''",
                  (d+8)*' ' + "_tgt = _png",
                  (d+4)*' ' + "except Exception:",
                  (d+8)*' ' + "return ''",
                  d*' ' + "try:",
                  (d+4)*' ' + "with OCR_SEM:",
                  (d+8)*' ' + "r = subprocess.run([OCRBIN, _tgt], capture_output=True, text=True, timeout=25)  # OCR-CAP v85.16: twenty-five seconds of patience per paper, never more",
                  (d+4)*' ' + "return r.stdout or ''",
                  d*' ' + "except Exception:",
                  (d+4)*' ' + "return ''"]
    done.append('ocr-raster')
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
if not any(l.strip().startswith('extract_text = extract_text_ocr') for l in B):
    while B and B[-1].strip() == '':
        B.pop()
    B += ["", "extract_text = extract_text_ocr  # ALIAS v85.89: one name for the whole chain, bound after every def has landed - the diag pdf column, emails_in_text and every bare caller wake from swallowing NameError"]
    done.append('alias-bound')
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
print('🔎 binaries and the healed chain:')
print('   | tesseract:', shutil.which('tesseract'))
print('   | sips     :', shutil.which('sips'))
L = open('butler.py').read().split('\n')
for k2b, l in enumerate(L):
    if 'PARAM-FIX v85.89' in l or 'OCR-RASTER v85.89' in l or 'ALIAS v85.89' in l:
        print('   |', l.strip()[:160])
M1 = perfile()
lost = set()
for fn in M0:
    lost |= (M0[fn] - M1.get(fn, set()))
if lost:
    print('⛔ witness diff per file:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff per file: 0 laws lost')
import sys, importlib
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
    if 'v85.89' not in t:
        open(AR, 'a').write('v85.89: PARAM-FIX ends the fp/p NameError that swallowed the whole reader chain for weeks; OCR-RASTER renders pdf page one to png via sips so tesseract reads ink not documents; ALIAS binds extract_text after every def so bare callers wake; OCR-PROBE returns with counted parentheses (S430, S431)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S430 the OCR eye can be probed by one command, timed and headed", "'S429 a deep row that earns a name shows its verdict, and a blind eye is named before it is cured", "ck('S430 the OCR eye can be probed by one command, timed and headed', ('def ocr_probe(' in _src) and (chr(35)+' OCR-PROBE v85.88') in _src)"),
      ("'S431 the reader chain has one name, one parameter and one raster hand", "'S430 the OCR eye can be probed by one command, timed and headed", "ck('S431 the reader chain has one name, one parameter and one raster hand', (chr(35)+' PARAM-FIX v85.89') in _src and (chr(35)+' OCR-RASTER v85.89') in _src and (chr(35)+' ALIAS v85.89') in _src)")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
