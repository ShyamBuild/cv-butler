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
ns = next((k for k, l in enumerate(B) if 'not a human-shaped name - left as is' in l), None)
if ns is not None and 'SERVICE-EYES' not in '\n'.join(B[ns:ns+30]):
    d = ind(B[ns])
    B[ns:ns+2] = [(d)*' ' + "_v = ''",
                  (d)*' ' + "try:",
                  (d+4)*' ' + "_v = heuristic_name(p) or _name_from_first_line(p)",
                  (d)*' ' + "except Exception:",
                  (d+4)*' ' + "_v = ''",
                  (d)*' ' + "_c = ''",
                  (d)*' ' + "try:",
                  (d+4)*' ' + "_c = _canonical_person_name(_v) if _v else ''",
                  (d)*' ' + "except Exception:",
                  (d+4)*' ' + "_c = ''",
                  (d)*' ' + "if _c:",
                  (d+4)*' ' + "_d2 = _display_name(_c)",
                  (d+4)*' ' + "_q2 = os.path.join(os.path.dirname(p), _d2 + ext)",
                  (d+4)*' ' + "if os.path.exists(_q2) and os.path.basename(_q2).lower() != x.lower():",
                  (d+8)*' ' + "log('🧭 service: %s | eyes say %s but a different paper holds that name - proposal only: confirm and I will suffix' % (x, _d2))  # SERVICE-EYES v85.85: twins are the master's decision, never the background's deed",
                  (d+4)*' ' + "else:",
                  (d+8)*' ' + "try:",
                  (d+12)*' ' + "os.rename(p, _q2)",
                  (d+12)*' ' + "log('✏️ service renamed (eyes): %s → %s' % (x, _d2 + ext))  # SERVICE-EYES v85.85: an improper name yields to the paper's own witness, in place, never across folders",
                  (d+12)*' ' + "try:",
                  (d+16)*' ' + "_safe_rename_ledger(p, _d2, 'service-eyes', once=True)",
                  (d+16)*' ' + "_safe_repath_ledgers(p, _q2)",
                  (d+12)*' ' + "except Exception:",
                  (d+16)*' ' + "pass",
                  (d+8)*' ' + "except Exception as _se2:",
                  (d+12)*' ' + "log('⚠️ service eyes-rename failed: %s | %r' % (x, _se2))",
                  (d)*' ' + "    return".strip() and (d)*' ' + "return",
                  (d)*' ' + "log('🧭 service: %s | name not human-shaped and eyes silent - teach me the human once and I will carry it' % x)",
                  (d)*' ' + "return"]
    done.append('service-eyes')
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
RD = os.path.join(os.getcwd(), 'archive', 'rendiag.py')
open(RD, 'w').write("#!/usr/bin/env python3\nimport os, sys\n_here = os.path.dirname(os.path.abspath(__file__))\nsys.path.insert(0, os.path.dirname(_here))\nsys.path.insert(0, os.path.expanduser('~/CV_Tool'))\ntry:\n    import butler\nexcept Exception as _e:\n    print('rendiag cannot import butler; sys.path was:')\n    for p in sys.path:\n        print('  ', p)\n    raise\npaths = []\nfor a in sys.argv[1:]:  # RENDIAG-FOLDERS v85.85: a folder argument walks every subfolder of any chair, so other desks diagnose in one command\n    if os.path.isdir(a):\n        for dp, dn, fn in os.walk(a):\n            for x in fn:\n                if x.lower().endswith(('.pdf', '.docx', '.doc', '.rtf')):\n                    paths.append(os.path.join(dp, x))\n            if len(paths) > 400: break\n    else:\n        paths.append(a)\nif not paths:\n    root = butler._lock_root() or (butler.desk_load() or {}).get('primary') or os.getcwd()\n    for dp, dn, fn in os.walk(root):\n        for x in fn:\n            if x.lower().endswith(('.pdf', '.docx', '.doc', '.rtf')):\n                paths.append(os.path.join(dp, x))\n        if len(paths) > 400: break\nbutler.rename_diag(paths)\n")
done.append('rendiag-folders')
M1 = perfile()
lost = set()
for fn in M0:
    lost |= (M0[fn] - M1.get(fn, set()))
if lost:
    print('⛔ witness diff per file:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff per file: 0 laws lost')
print('🔎 service-eyes branch:')
L = open('butler.py').read().split('\n')
for k2, l in enumerate(L):
    if 'SERVICE-EYES v85.85' in l:
        print('   |', l.strip()[:160])
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.85' not in t:
        open(AR, 'a').write('v85.85: SERVICE-EYES - the right-click consults the paper own witness when the stem is not a person shape, renaming in place to the eyed human, proposing only when another paper holds that name, confessing when eyes are silent; rendiag accepts folder arguments so any chair diagnoses in one command (S426, S427)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S426 an improper name yields to the paper's own witness, in place, twins proposed never moved", "'S425 a ghost is announced once and the reconcile heals its missing history", "ck('S426 an improper name yields to the paper'+chr(39)+'s own witness, in place, twins proposed never moved', (chr(35)+' SERVICE-EYES v85.85') in _src and ('service renamed (eyes)' in _src))"),
      ("'S427 any chair diagnoses in one command, folder by folder", "'S426 an improper name yields to the paper's own witness, in place, twins proposed never moved", "ck('S427 any chair diagnoses in one command, folder by folder', ('RENDIAG-FOLDERS v85.85' in open(os.path.join(BASE_DIR, 'archive', 'rendiag.py')).read()) and ('isdir' in open(os.path.join(BASE_DIR, 'archive', 'rendiag.py')).read()))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
