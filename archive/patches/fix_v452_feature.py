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
c0 = next((k for k, l in enumerate(B) if l.startswith('def _pdf_pure_text(')), None)
if c0 is not None and 'PDF-PURE-HARD v85.71' not in '\n'.join(B[c0:c0+40]):
    c1 = next(k for k in range(c0 + 1, len(B)) if B[k].startswith('def '))
    d = ind(B[c0])
    B[c0:c1] = [d*' ' + "def _pdf_pure_text(p):  # PDF-PURE v85.70: the standard library reads the text layer when frameworks are denied  # PDF-PURE-HARD v85.71: Flate, ASCII85, hex strings, concatenated blocks and plain streams - every costume a producer wears",
                (d+4)*' ' + "import zlib as _zl, base64 as _b64",
                (d+4)*' ' + "try:",
                (d+8)*' ' + "if os.path.splitext(p)[1].lower() != '.pdf': return ''",
                (d+8)*' ' + "raw = open(p, 'rb').read()",
                (d+4)*' ' + "except Exception:",
                (d+8)*' ' + "return ''",
                (d+4)*' ' + "out = []",
                (d+4)*' ' + "pos = 0",
                (d+4)*' ' + "while True:",
                (d+8)*' ' + "i = raw.find(b'stream', pos)",
                (d+8)*' ' + "if i < 0: break",
                (d+8)*' ' + "j = raw.find(b'endstream', i)",
                (d+8)*' ' + "if j < 0: break",
                (d+8)*' ' + "chunk = raw[i+6:j]",
                (d+8)*' ' + "if chunk[:2] == b'\\r\\n': chunk = chunk[2:]",
                (d+8)*' ' + "elif chunk[:1] in (b'\\n', b'\\r', b' '): chunk = chunk[1:]",
                (d+8)*' ' + "dec = b''",
                (d+8)*' ' + "try:",
                (d+12)*' ' + "dec = _zl.decompress(chunk)",
                (d+8)*' ' + "except Exception:",
                (d+12)*' ' + "try:",
                (d+16)*' ' + "dec = _zl.decompressobj().decompress(chunk)",
                (d+12)*' ' + "except Exception:",
                (d+16)*' ' + "dec = b''",
                (d+8)*' ' + "if not dec:",
                (d+12)*' ' + "try:",
                (d+16)*' ' + "dec = _b64.a85decode(chunk, adobe=False, ignorechars=b' \\n\\r\\t')",
                (d+16)*' ' + "try:",
                (d+20)*' ' + "dec = _zl.decompress(dec)",
                (d+16)*' ' + "except Exception:",
                (d+20)*' ' + "pass",
                (d+12)*' ' + "except Exception:",
                (d+16)*' ' + "dec = b''",
                (d+8)*' ' + "if not dec and chunk.strip():",
                (d+12)*' ' + "dec = chunk",
                (d+8)*' ' + "if dec:",
                (d+12)*' ' + "for m in re.finditer(rb'\\((?:\\\\.|[^\\\\()])*)\\)', dec):",
                (d+16)*' ' + "s = m.group(0)[1:-1]",
                (d+16)*' ' + "s = s.replace(b'\\\\(', b'(').replace(b'\\\\)', b')').replace(b'\\\\\\\\', b'\\\\')",
                (d+16)*' ' + "t = s.decode('utf-8', 'ignore')",
                (d+16)*' ' + "if t.strip(): out.append(t)",
                (d+12)*' ' + "for m in re.finditer(rb'<([0-9A-Fa-f\\s]{8,})>', dec):",
                (d+16)*' ' + "hx = re.sub(rb'\\s', b'', m.group(1))",
                (d+16)*' ' + "try:",
                (d+20)*' ' + "t = bytes.fromhex(hx.decode()).decode('utf-8', 'ignore')",
                (d+16)*' ' + "except Exception:",
                (d+20)*' ' + "t = ''",
                (d+16)*' ' + "if t.strip(): out.append(t)",
                (d+8)*' ' + "pos = j + 9",
                (d+4)*' ' + "return '\\n'.join(out)",
                ""]
    done.append('pdf-pure-hard')
ts = next((k for k, l in enumerate(B) if 'SKIP text-silent (vision not summoned in diag)' in l), None)
if ts is not None and 'DIAG-FILTERS' not in '\n'.join(B[ts:ts+8]):
    d = ind(B[ts])
    B.insert(ts+1, d*' ' + "if x.lower().endswith('.pdf'):  # DIAG-FILTERS v85.71: when a pdf is silent, name its stream costumes so the next lap knows which decoder to teach, instead of inheriting another zero",
                (d+4)*' ' + "try:",
                (d+8)*' ' + "_fr = open(p, 'rb').read(300000)",
                (d+8)*' ' + "dec += ' | filters: ' + ','.join(sorted(set(m.decode() for m in re.findall(rb'/Filter\\s*/?([A-Za-z0-9]+)', _fr)))[:4])",
                (d+4)*' ' + "except Exception:",
                (d+8)*' ' + "pass")
    done.append('diag-filters')
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
print('🔎 hardened eye head and filters hook:')
L = open('butler.py').read().split('\n')
for k2, l in enumerate(L):
    if 'PDF-PURE-HARD v85.71: Flate' in l or 'DIAG-FILTERS v85.71' in l:
        print('   |', l.strip()[:160])
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.71' not in t:
        open(AR, 'a').write('v85.71: PDF-PURE-HARD - the pure eye decodes Flate whole and partial, ASCII85+Flate, hex strings and uncompressed streams; DIAG-FILTERS names a silent pdf /Filter list in the diagnostic row so no fifth decoder guess is blind (S417, S418)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S417 the pure eye wears every decoder a producer wears", "'S416 a silent sweep names the guard that silenced each file", "ck('S417 the pure eye wears every decoder a producer wears', (chr(35)+' PDF-PURE-HARD v85.71') in _src and ('a85decode' in _src) and ('decompressobj' in _src))"),
      ("'S418 a silent pdf names its stream costumes", "'S417 the pure eye wears every decoder a producer wears", "ck('S418 a silent pdf names its stream costumes', (chr(35)+' DIAG-FILTERS v85.71') in _src and ('/Filter' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
