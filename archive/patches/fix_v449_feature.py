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
jk = next((k for k, l in enumerate(B) if "ObjC.import(\"Quartz\"); var d = $.PDFDocument" in l), None)
if jk is not None and 'ObjC.import("PDFKit")' not in B[jk]:
    B[jk] = B[jk].replace('ObjC.import("Quartz");', 'ObjC.import("PDFKit"); ObjC.import("Quartz");', 1)
    done.append('pdfkit-import-hardened')
dk = next((k for k, l in enumerate(B) if l.strip().startswith("say('🔎 %s | word=%d pdf=%d")), None)
if dk is not None and 'DIAG-STDERR' not in '\n'.join(B[dk-6:dk+2]):
    d = ind(B[dk])
    B[dk:dk] = [d*' ' + "_perr = ''",
                d*' ' + "if x.lower().endswith('.pdf') and not wt.strip() and not tt.strip():  # DIAG-STDERR v85.68: a silent pdf row carries the osascript complaint, so the next receipt names the failure instead of another zero",
                (d+4)*' ' + "try:",
                (d+8)*' ' + "import subprocess as _sp7",
                (d+8)*' ' + "_pj7 = p.replace('\\\\', '\\\\\\\\').replace('\"', '\\\\\"')",
                (d+8)*' ' + "_js7 = 'ObjC.import(\"PDFKit\"); ObjC.import(\"Quartz\"); var d = $.PDFDocument.alloc.initWithURL($.NSURL.fileURLWithPath(\"' + _pj7 + '\")); (d.isNil() || !d.string) ? \"\" : d.string.js'",
                (d+8)*' ' + "_r7 = _sp7.run(['osascript', '-l', 'JavaScript', '-e', _js7], capture_output=True, timeout=60)",
                (d+8)*' ' + "_perr = (_r7.stderr.decode('utf-8', 'ignore') or '')[:80].strip()",
                (d+4)*' ' + "except Exception as _e7:",
                (d+8)*' ' + "_perr = repr(_e7)[:80]",
                d*' ' + "if _perr: dec += ' | pdfkit-err: ' + _perr"]
    done.append('diag-stderr')
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
print('🔎 backup evidence (cv-memory / tgz / iCloud / Mobile Documents), verbatim:')
for fn in ('butler.py', 'briefing.py'):
    for k, l in enumerate(open(fn).read().split('\n')):
        if any(s in l for s in ('cv-memory', '.tgz', 'iCloud', 'Mobile Documents')):
            print('   |', fn, k+1, '|', l.strip()[:170])
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.68' not in t:
        open(AR, 'a').write('v85.68: DIAG-STDERR - a silent pdf row carries the osascript stderr so failures name themselves; PDFKit imported beside Quartz; backup evidence printed verbatim for next lap exact redirect to ~/Backup of Butler (S412)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S412 a silent pdf row carries the complaint that silenced it", "'S411 every pdf has a native text eye that needs no index and no pixels", "ck('S412 a silent pdf row carries the complaint that silenced it', (chr(35)+' DIAG-STDERR v85.68') in _src and ('pdfkit-err' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
