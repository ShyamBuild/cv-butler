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
dg = next((k for k, l in enumerate(B) if l.startswith('def rename_diag(')), None)
if dg is not None and 'deep=False' not in B[dg]:
    B[dg] = B[dg].replace('def rename_diag(paths, say=print):', 'def rename_diag(paths, say=print, deep=False):  # RENDIAG-DEEP v85.86: opt-in depth - a silent row may summon the capped OCR eye for its first-line name, because tuning needs the datum the fast table refuses to pay for')
    done.append('diag-deep-sig')
fg = next((k for k, l in enumerate(B) if l.strip() == 'if txt.strip():' and k > (dg or 0)), None)
if fg is not None and 'deep' not in B[fg]:
    d = ind(B[fg])
    B[fg] = d*' ' + "if txt.strip() or deep:  # RENDIAG-DEEP v85.86: in deep mode the first-line eye may pay the OCR cap for silent papers"
    done.append('diag-deep-gate')
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
RD = os.path.join(os.getcwd(), 'archive', 'rendiag.py')
open(RD, 'w').write("#!/usr/bin/env python3\nimport os, sys\n_here = os.path.dirname(os.path.abspath(__file__))\nsys.path.insert(0, os.path.dirname(_here))\nsys.path.insert(0, os.path.expanduser('~/CV_Tool'))\ntry:\n    import butler\nexcept Exception as _e:\n    print('rendiag cannot import butler; sys.path was:')\n    for p in sys.path:\n        print('  ', p)\n    raise\ndeep = '--deep' in sys.argv[1:]\nargs = [a for a in sys.argv[1:] if a != '--deep']\npaths = []\nfor a in args:  # RENDIAG-FOLDERS v85.85: a folder argument walks every subfolder of any chair, so other desks diagnose in one command\n    if os.path.isdir(a):\n        for dp, dn, fn in os.walk(a):\n            for x in fn:\n                if x.lower().endswith(('.pdf', '.docx', '.doc', '.rtf')):\n                    paths.append(os.path.join(dp, x))\n            if len(paths) > 400: break\n    else:\n        paths.append(a)\nif not paths:\n    root = butler._lock_root() or (butler.desk_load() or {}).get('primary') or os.getcwd()\n    for dp, dn, fn in os.walk(root):\n        for x in fn:\n            if x.lower().endswith(('.pdf', '.docx', '.doc', '.rtf')):\n                paths.append(os.path.join(dp, x))\n        if len(paths) > 400: break\ntry:\n    butler.rename_diag(paths, deep=deep)\nexcept BrokenPipeError:  # PIPE-GRACE v85.86: when the reader stops listening (head, less, a closed window), the table dies quietly instead of tracebacking over its own rows\n    os._exit(0)\n")
done.append('rendiag-deep-pipe')
M1 = perfile()
lost = set()
for fn in M0:
    lost |= (M0[fn] - M1.get(fn, set()))
if lost:
    print('⛔ witness diff per file:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff per file: 0 laws lost')
print('🔎 deep signature and gate:')
L = open('butler.py').read().split('\n')
for k2, l in enumerate(L):
    if 'RENDIAG-DEEP v85.86' in l:
        print('   |', l.strip()[:160])
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.86' not in t:
        open(AR, 'a').write('v85.86: RENDIAG-DEEP opt-in OCR column for silent rows so other chairs tune at full depth; rendiag exits quietly on BrokenPipeError; SERVICE-EYES already reaches the OCR eye through _name_from_first_line, so right-click renames misnamed scans in place within the 25s cap (S428)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S428 depth is a choice the master makes, and a closed pipe is a quiet goodbye", "'S427 any chair diagnoses in one command, folder by folder", "ck('S428 depth is a choice the master makes, and a closed pipe is a quiet goodbye', (chr(35)+' RENDIAG-DEEP v85.86') in _src and ('BrokenPipeError' in open(os.path.join(BASE_DIR, 'archive', 'rendiag.py')).read()))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
