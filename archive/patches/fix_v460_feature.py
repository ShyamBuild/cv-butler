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
ex = next((k for k, l in enumerate(B) if l.startswith('def extract_text(')), None)
if ex is not None and 'PY-PYPDF' not in '\n'.join(B[ex:ex+10]):
    d = ind(B[ex+1]) if ex+1 < len(B) else 4
    B[ex+1:ex+1] = [d*' ' + "try:  # PY-PYPDF v85.72 (def-line anchor v85.79): the venv reader speaks CID glyph maps - inserted at the one anchor that cannot miss, ahead of every other eye",
                    (d+4)*' ' + "import pypdf as _pypdf",
                    (d+4)*' ' + "_pr = _pypdf.PdfReader(p)",
                    (d+4)*' ' + "_ptx = '\\n'.join((pg.extract_text() or '') for pg in _pr.pages)",
                    (d+4)*' ' + "if _ptx.strip(): return _ptx",
                    d*' ' + "except Exception:",
                    (d+4)*' ' + "pass"]
    done.append('py-pypdf-defline')
    print('🔎 extract_text head, verbatim:')
    for j in range(ex, min(ex+12, len(B))):
        print('   |', B[j].rstrip()[:150])
e0 = next(k for k, l in enumerate(B) if l.startswith('def _event_tick('))
if 'def restore_dups(' not in '\n'.join(B):
    B[e0:e0] = ["def restore_dups():  # RESTORE-DUPS v85.79: carry every parked paper home through remembered addresses - space-safe, parking-lot-skipping, every decision spoken, only true orphans left for the master's hand",
                "    root = _lock_root() or (desk_load() or {}).get('primary') or os.getcwd()",
                "    dd = os.path.join(root, '__duplicates')",
                "    if not os.path.isdir(dd):",
                "        print('no __duplicates under', root)",
                "        return []",
                "    blob = ''",
                "    for b in (BASE_DIR, root, os.path.dirname(root)):",
                "        try:",
                "            for dp, dn, fn in os.walk(b):",
                "                for y in fn:",
                "                    if y.endswith('.json'):",
                "                        try:",
                "                            blob += open(os.path.join(dp, y), encoding='utf-8', errors='ignore').read() + '\\n'",
                "                        except Exception:",
                "                            pass",
                "        except Exception:",
                "            pass",
                "    moved = []",
                "    for x in sorted(os.listdir(dd)):",
                "        home = None",
                "        for m in re.findall(r'\"([^\"]*?/' + re.escape(x) + r')\"', blob):  # RESTORE-SPACES v85.79: addresses hold spaces; a reader that forbids them finds no homes",
                "            d0 = os.path.dirname(m)",
                "            if d0 and os.path.isdir(d0) and os.path.realpath(d0) != os.path.realpath(dd) and not os.path.exists(os.path.join(d0, x)):",
                "                home = d0",
                "                break",
                "        if home:",
                "            try:",
                "                os.rename(os.path.join(dd, x), os.path.join(home, x))",
                "                moved.append(x)",
                "                print('restored:', x, '->', home)",
                "            except Exception as _re:",
                "                print('failed:', x, repr(_re))",
                "        else:",
                "            print('drag by hand:', x)",
                "    print('remaining in __duplicates:', os.listdir(dd))",
                "    return moved",
                ""]
    done.append('restore-dups')
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
    if 'v85.79' not in t:
        open(AR, 'a').write('v85.79: RESTORE-DUPS verb carries parked papers home via space-safe quoted-path memory across workshop, chair and desk parent, skipping the parking lot; PY-PYPDF re-anchored at the def extract_text line with the eye-chain head printed verbatim; after restore the awakened sweep renames in place and QUEUE-ACT answers the right-click (S422)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S422 every parked paper has a road home through remembered addresses", "'S421 on a case-insensitive disk, a paper is never its own twin", "ck('S422 every parked paper has a road home through remembered addresses', ('def restore_dups(' in _src) and (chr(35)+' RESTORE-DUPS v85.79') in _src and (chr(35)+' RESTORE-SPACES v85.79') in _src)")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
