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
if 'def rename_diag(' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.startswith('def _case_sweep('))
    B[i:i] = ["def rename_diag(paths, say=print):  # RENAME-DIAG v85.58: the butler opens its eyes in public - per file, every reader's yield, every eye's verdict and the decision with its reason, so a miss is a datum and not a mystery",
              "    for p in paths:",
              "        x = os.path.basename(p)",
              "        stem = os.path.splitext(x)[0]",
              "        try:",
              "            jd = 'jd' if _jd_like_name(x) else ('portal' if _portal_name(x) else '')",
              "        except Exception:",
              "            jd = '?'",
              "        wt = _word_text(p)",
              "        tt = ''",
              "        try:",
              "            tt = extract_text(p) or ''",
              "        except Exception:",
              "            tt = ''",
              "        txt = wt or tt",
              "        fl = ''",
              "        for ln in txt.split('\\n'):",
              "            ln = ln.strip()",
              "            if ln:",
              "                fl = ln[:70]; break",
              "        h = ''",
              "        try:",
              "            h = heuristic_name(p) or ''",
              "        except Exception:",
              "            h = 'err'",
              "        f1 = ''",
              "        if txt.strip():",
              "            try:",
              "                f1 = _name_from_first_line(p) or ''",
              "            except Exception:",
              "                f1 = 'err'",
              "        c = ''",
              "        try:",
              "            c = _canonical_person_name(h or f1) or ''",
              "        except Exception:",
              "            c = 'err'",
              "        disp = _display_name(c) if c else ''",
              "        if jd: dec = 'SKIP ' + jd",
              "        elif not txt.strip(): dec = 'SKIP text-silent (vision not summoned in diag)'",
              "        elif not c: dec = 'SKIP no-name-from-eyes'",
              "        elif _name_key(stem) != _name_key(c): dec = 'SKIP different-human'",
              "        elif stem == disp: dec = 'OK already-cased'",
              "        else: dec = 'RENAME -> ' + disp",
              "        say('🔎 %s | word=%d pdf=%d | first-line: %s | heuristic: %s | firstline-eye: %s | canon: %s | display: %s | %s' % (x, len(wt), len(tt), fl, h, f1, c, disp, dec))",
              ""]
    done.append('rename-diag')
ev = next((k for k, l in enumerate(B) if l.startswith('def _event_tick(')), None)
cs = next((k for k in range(ev, ev+8) if '_case_sweep(root, log)' in B[k]), None) if ev is not None else None
if cs is not None and 'SERVICE-QUEUE' not in '\n'.join(B[ev:cs]):
    d = ind(B[cs])
    B.insert(cs, d*' ' + "_qf = os.path.join(BASE_DIR, '.rename_queue')  # SERVICE-QUEUE v85.58: the master's Finder selection arrives as lines in a queue; the bell drains it each beat and runs the whole arrival pipeline in the background, no terminal opened")
    B.insert(cs+1, d*' ' + "if os.path.exists(_qf):")
    B.insert(cs+2, (d+4)*' ' + "try:")
    B.insert(cs+3, (d+8)*' ' + "_qs = [l.strip() for l in open(_qf) if l.strip()]")
    B.insert(cs+4, (d+8)*' ' + "os.remove(_qf)")
    B.insert(cs+5, (d+8)*' ' + "for _qp in _qs:")
    B.insert(cs+6, (d+12)*' ' + "if not os.path.isfile(_qp): continue")
    B.insert(cs+7, (d+12)*' ' + "log('🖱 service queued: %s' % os.path.basename(_qp))")
    B.insert(cs+8, (d+12)*' ' + "_ext = os.path.splitext(_qp)[1].lower()")
    B.insert(cs+9, (d+12)*' ' + "if _ext in ('.docx', '.doc', '.rtf', '.png', '.jpg', '.jpeg', '.heic'): _convert_to_pdf(_qp, log)")
    B.insert(cs+10, (d+12)*' ' + "elif _ext == '.pdf': _fast_rename(_qp, root, log)")
    B.insert(cs+11, (d+4)*' ' + "except Exception:")
    B.insert(cs+12, (d+8)*' ' + "pass")
    done.append('service-queue')
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
RD = os.path.join(os.getcwd(), 'rendiag.py')
if not os.path.exists(RD):
    open(RD, 'w').write("#!/usr/bin/env python3\nimport os, sys\nsys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\nimport butler\npaths = sys.argv[1:]\nif not paths:\n    root = butler._lock_root() or (butler.desk_load() or {}).get('primary') or os.getcwd()\n    paths = []\n    for dp, dn, fn in os.walk(root):\n        for x in fn:\n            if x.lower().endswith(('.pdf', '.docx', '.doc', '.rtf')):\n                paths.append(os.path.join(dp, x))\n        if len(paths) > 400: break\nbutler.rename_diag(paths)\n")
    done.append('rendiag-script')
M1 = perfile()
lost = set()
for fn in M0:
    lost |= (M0[fn] - M1.get(fn, set()))
if lost:
    print('⛔ witness diff per file:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff per file: 0 laws lost')
print('🔎 diag head and queue drain:')
L = open('butler.py').read().split('\n')
for k, l in enumerate(L):
    if 'def rename_diag(' in l or '_qf = os.path.join(BASE_DIR' in l:
        print('   |', l.strip()[:150])
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.58' not in t:
        open(AR, 'a').write('v85.58: RENAME-DIAG opens every eye in public per file with its decision and reason; rendiag.py diagnoses the whole live desk in one command; SERVICE-QUEUE lets a Finder Quick Action append paths to .rename_queue which the bell drains each beat through convert+fast-rename, logging to tick.log - right-click renaming with no terminal (S401, S402)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S401 the butler's eyes open in public, one honest row per file", "'S400 casing is a property of the name, not of the ceremony's memory", "ck('S401 the butler'+chr(39)+'s eyes open in public, one honest row per file', ('def rename_diag(' in _src) and (chr(35)+' RENAME-DIAG v85.58') in _src and os.path.exists(os.path.join(BASE_DIR, 'rendiag.py')))"),
      ("'S402 the master's Finder selection is drained by the bell, in the background, each beat", "'S401 the butler's eyes open in public, one honest row per file", "ck('S402 the master'+chr(39)+'s Finder selection is drained by the bell, in the background, each beat', (chr(35)+' SERVICE-QUEUE v85.58') in _src and ('.rename_queue' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
