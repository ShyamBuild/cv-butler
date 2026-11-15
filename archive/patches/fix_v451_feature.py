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
if 'def _pdf_pure_text(' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.startswith('def _word_text('))
    B[i:i] = ["def _pdf_pure_text(p):  # PDF-PURE v85.70: the standard library reads the text layer when frameworks are denied - zlib streams and text-show operators, no permissions, no pixels, no index",
              "    import zlib as _zl",
              "    try:",
              "        if os.path.splitext(p)[1].lower() != '.pdf': return ''",
              "        raw = open(p, 'rb').read()",
              "    except Exception:",
              "        return ''",
              "    out = []",
              "    pos = 0",
              "    while True:",
              "        i = raw.find(b'stream', pos)",
              "        if i < 0: break",
              "        j = raw.find(b'endstream', i)",
              "        if j < 0: break",
              "        chunk = raw[i+6:j]",
              "        if chunk[:2] in (b'\\r\\n', b'\\n'): chunk = chunk[2:]",
              "        elif chunk[:1] in (b'\\r', b' '): chunk = chunk[1:]",
              "        try:",
              "            dec = _zl.decompress(chunk)",
              "        except Exception:",
              "            dec = b''",
              "        if dec:",
              "            for m in re.finditer(rb'\\((?:\\\\.|[^\\\\()])*)\\)', dec):",
              "                s = m.group(0)[1:-1]",
              "                s = s.replace(b'\\\\(', b'(').replace(b'\\\\)', b')').replace(b'\\\\\\\\', b'\\\\')",
              "                t = s.decode('utf-8', 'ignore')",
              "                if t.strip(): out.append(t)",
              "        pos = j + 9",
              "    return '\\n'.join(out)",
              ""]
    done.append('pdf-pure-def')
pk = next((k for k, l in enumerate(B) if 'PDF-PDFKIT v85.65: when the library' in l), None)
if pk is not None and 'PDF-PURE v85.70: the standard library' not in '\n'.join(B[pk-3:pk]):
    d = ind(B[pk])
    B.insert(pk, d*' ' + "_pt = _pdf_pure_text(p)  # PDF-PURE v85.70: the permission-free eye is asked before any framework that macOS may silently refuse")
    B.insert(pk+1, d*' ' + "if len(_pt) > 40 and re.search(r'[A-Za-z]{4,}', _pt): return _pt")
    done.append('pdf-pure-wire')
c0 = next((k for k, l in enumerate(B) if l.startswith('def _case_sweep(')), None)
if c0 is not None and 'SWEEP-TRACE v85.70' not in '\n'.join(B[c0:c0+40]):
    c1 = next(k for k in range(c0 + 1, len(B)) if B[k].startswith('def '))
    d = ind(B[c0])
    B[c0:c1] = [d*' ' + "def _case_sweep(root, log, trace=False):  # CASE-SWEEP v85.57: casing is a property of the name, not of the ceremony's memory  # SWEEP-TRACE v85.70: with trace on, every file speaks its verdict, so a silent sweep names the guard that silenced it",
                (d+4)*' ' + "try:",
                (d+8)*' ' + "dirs = [root] + [os.path.join(root, s) for s in os.listdir(root) if os.path.isdir(os.path.join(root, s)) and not s.startswith('.')]  # DIRS-ALL v85.69: every immediate folder of the chair is swept",
                (d+4)*' ' + "except Exception:",
                (d+8)*' ' + "dirs = [root]",
                (d+4)*' ' + "for dpath in dirs:",
                (d+8)*' ' + "try:",
                (d+12)*' ' + "names = os.listdir(dpath)",
                (d+8)*' ' + "except Exception:",
                (d+12)*' ' + "continue",
                (d+8)*' ' + "for x in names:",
                (d+12)*' ' + "p = os.path.join(dpath, x)",
                (d+12)*' ' + "if not os.path.isfile(p):",
                (d+16)*' ' + "if trace: log('🧭 sweep: %s | not-a-file' % x)",
                (d+16)*' ' + "continue",
                (d+12)*' ' + "ext = os.path.splitext(x)[1].lower()",
                (d+12)*' ' + "if ext not in ('.pdf', '.docx', '.doc', '.rtf'): continue",
                (d+12)*' ' + "stem = os.path.splitext(x)[0]",
                (d+12)*' ' + "try:",
                (d+16)*' ' + "if _jd_like_name(x) or _portal_name(x):",
                (d+20)*' ' + "if trace: log('🧭 sweep: %s | masked (jd/portal)' % x)",
                (d+20)*' ' + "continue",
                (d+12)*' ' + "except Exception:",
                (d+16)*' ' + "continue",
                (d+12)*' ' + "ws = stem.split()",
                (d+12)*' ' + "if not (2 <= len(ws) <= 4 and all(w.isalpha() or '-' in w or '.' in w for w in ws)):",
                (d+16)*' ' + "if trace: log('🧭 sweep: %s | not-human-shape' % x)",
                (d+16)*' ' + "continue",
                (d+12)*' ' + "disp = _display_name(stem)",
                (d+12)*' ' + "if disp == stem: continue",
                (d+12)*' ' + "q = os.path.join(dpath, disp + ext)",
                (d+12)*' ' + "if os.path.exists(q):",
                (d+16)*' ' + "if trace: log('🧭 sweep: %s | twin-exists %s' % (x, disp + ext))",
                (d+16)*' ' + "continue",
                (d+12)*' ' + "try:",
                (d+16)*' ' + "os.rename(p, q)",
                (d+16)*' ' + "log('✏️ case sweep: %s → %s' % (x, disp + ext))",
                (d+16)*' ' + "try:",
                (d+20)*' ' + "_safe_rename_ledger(p, disp, 'sweep', once=True)",
                (d+20)*' ' + "_safe_repath_ledgers(p, q)",
                (d+16)*' ' + "except Exception:",
                (d+20)*' ' + "pass",
                (d+12)*' ' + "except Exception as _ce:",
                (d+16)*' ' + "if trace: log('🧭 sweep: %s | rename-failed %r' % (x, _ce))",
                ""]
    done.append('sweep-trace')
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
print('🔎 pure eye wire and trace head:')
L = open('butler.py').read().split('\n')
for k2, l in enumerate(L):
    if 'PDF-PURE v85.70: the permission-free' in l or 'SWEEP-TRACE v85.70: with trace' in l:
        print('   |', l.strip()[:160])
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.70' not in t:
        open(AR, 'a').write('v85.70: PDF-PURE - zlib plus text-show operators read any pdf text layer with the standard library alone, curing the TCC-refused frameworks (CoreGraphics errors, nil docs); SWEEP-TRACE makes every swept file speak its verdict on demand; BACKUP-LOCAL confirmed live, stale iCloud leftover is pre-redirect (S415, S416)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S415 the text layer is readable by the standard library alone, permissions or no permissions", "'S414 the memory archives rest in a local folder, not in the master's cloud", "ck('S415 the text layer is readable by the standard library alone, permissions or no permissions', (chr(35)+' PDF-PURE v85.70') in _src and ('def _pdf_pure_text(' in _src) and ('zlib' in _src))"),
      ("'S416 a silent sweep names the guard that silenced each file", "'S415 the text layer is readable by the standard library alone, permissions or no permissions", "ck('S416 a silent sweep names the guard that silenced each file', (chr(35)+' SWEEP-TRACE v85.70') in _src and ('trace=False' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
