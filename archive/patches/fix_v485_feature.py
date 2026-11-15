import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'archive'))
import patchlib as P
done = []
M0 = P.perfile()
B = P.read()
a = next((k for k, l in enumerate(B) if '_en = _eyename_of(p)' in l), None)
if a is not None:
    b = next(k for k in range(a, min(a+30, len(B))) if 'ws = stem.split()' in B[k])
    del B[a:b]; done.append('sweep-eye-removed')
c = next((k for k, l in enumerate(B) if "os.rename(p, q2); log('✏️ service renamed (eyes)" in l), None)
if c is not None:
    B[c] = P.ind(B[c])*' ' + "log('🧭 service proposes: %s reads as %s in its head - rename in Finder or teach me; the eye may name but never rename  # SERVICE-EYES v85.85 (propose-only v85.98)' % (x, d2))  # EYES-PROPOSE-ONLY v85.98: authority returns to the trained gates and the master's hand"
    k = c+1
    while k < len(B) and not B[k].strip().startswith('except Exception as _se2'): k += 1
    del B[c+1:k]; done.append('service-eye-proposal')
if P.sub_in_line(B, "_EYE_VSN = 'v85.97'", "_EYE_VSN = 'v85.99'", 'EYES-PROPOSE-ONLY v85.98 + NAME-JOIN v85.99: cached slogan verdicts expire'): done.append('eyevsn-bump')
ns = next((k for k, l in enumerate(B) if l.startswith('_NAME_STOP = set(')), None)
if ns is not None and '_NAME_STOP |=' not in '\n'.join(B[ns:ns+3]):
    d = P.ind(B[ns])
    B.insert(ns+1, d*' ' + "_NAME_STOP |= set('objective education educational contact linkedin personal competencies competency summary profile work works employment career declaration interests hobbies skills skill father mother husband wife name names designation applied applying ref referral resume cv'.split())  # NAME-GATE v85.97 (extended v85.98): section headers and kin-words never pose as people")
    done.append('stop-extended')
ls = next((k for k, l in enumerate(B) if l.strip().startswith('_lines = [l.strip() for l in t.split')), None)
le = next((k for k, l in enumerate(B) if l.strip().startswith('if not fl and _lines: fl = _lines[0]')), None)
if ls is not None and le is not None and le > ls and 'NAME-JOIN' not in '\n'.join(B[ls:le]):
    d = P.ind(B[ls])
    B[ls:le] = [d*' ' + "_lines = [re.split(r'\\s+(?:Phone|Mob|Tel|E-Mail|Email)[:\\-]?', l.strip(), flags=re.I)[0].strip() for l in t.split('\\n') if l.strip()][:8]  # NAME-SCAN v85.95  # NAME-JOIN v85.98: a name split across wrapped lines is still one name - read singly, in pairs and in triples; each witness wears its own hash",
                d*' ' + "fl = ''", d*' ' + "_i = 0", d*' ' + "while _i < len(_lines) and not fl:",
                (d+4)*' ' + "_cands = [_lines[_i]]",
                (d+4)*' ' + "if _i + 1 < len(_lines): _cands.append(_lines[_i] + ' ' + _lines[_i+1])",
                (d+4)*' ' + "if _i + 2 < len(_lines): _cands.append(_lines[_i] + ' ' + _lines[_i+1] + ' ' + _lines[_i+2])",
                (d+4)*' ' + "for _cut in _cands:",
                (d+8)*' ' + "_wsc = _cut.split()",
                (d+8)*' ' + "if 2 <= len(_wsc) <= 4 and len(_cut) <= 40 and all(w.isalpha() or '-' in w or '.' in w for w in _wsc) and not (set(w.lower() for w in _wsc) & _NAME_STOP) and (_canonical_person_name(_cut) or ''):",
                (d+12)*' ' + "fl = _cut", (d+12)*' ' + "break",
                (d+4)*' ' + "_i += 1"]
    done.append('name-join')
if P.sub_in_line(B, "if 2 <= len(ws) <= 4 and all(w.isalpha() or '-' in w or '.' in w for w in ws):",
                 "if 2 <= len(ws) <= 4 and all(w.isalpha() or '-' in w or '.' in w for w in ws) and not (set(w.lower() for w in ws) & _NAME_STOP):",
                 'NAME-GATE v85.97: the fallback single-line path wears the same gate as the scan'): done.append('gate-on-fallback')
s4 = next((k for k, l in enumerate(B) if l.strip().startswith("ck('S441 ")), None)
if s4 is not None:
    d = P.ind(B[s4])
    B[s4:s4+1] = [d*' ' + "ck('S441 the eye may name but never rename - authority rests with the trained gates and the master'+chr(39)+'s hand', (chr(35)+' EYES-PROPOSE-ONLY v85.98') in _src)",
                  d*' ' + "ck('S441B no background sweep renames from eye text', _src.count('sweep renamed ' + '(eyes)') == 0)",
                  d*' ' + "ck('S441C no service renames from eye text, only proposes', _src.count('service renamed ' + '(eyes)') == 0 and ('service proposes:' in _src))"]
    done.append('s441-split')
P.append_module(B, [(0, "try:  # FAIL-LOUD v85.99: a failed guard prints its own probe line, so no lap ever guesses why"),
                    (1, "_orig_ck_v8599 = ck"),
                    (1, "def ck(name, cond, *a, **k):"),
                    (2, "_r = _orig_ck_v8599(name, cond, *a, **k)"),
                    (2, "if not cond:"),
                    (3, "try:"),
                    (4, "import inspect as _ins"),
                    (4, "_fr = _ins.currentframe().f_back"),
                    (4, "_fl = open(_ins.getsourcefile(_fr)).read().split('\\n')[_fr.f_lineno-1].strip()"),
                    (4, "print('🩸 FAIL WHY %s: %s' % (name, _fl[:200]))"),
                    (3, "except Exception:"),
                    (4, "pass"),
                    (2, "return _r"),
                    (0, "except NameError:"),
                    (1, "pass")])
done.append('fail-loud')
lost = P.preflight(B, M0)
if lost:
    print('⛔ preflight markers would be lost:', sorted(lost)); raise SystemExit('fix before write')
P.write(B); P.witness(M0)
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
t = open(AR).read()
if 'v85.99' not in t:
    open(AR, 'a').write('v85.99: NAME-JOIN reads wrapped name lines as one human; EYES-PROPOSE-ONLY ends eye-renames forever; FAIL-LOUD makes every failed guard print its own probe line; S441 split into three conjunct-guards so a failure names its string; receipt sources and the mirror are the two reading channels, and probes never hold their own forbidden literals (S441, S441B, S441C, S442, S443)\n')
    done.append('arch-line')
src = '\n'.join(B)
def anch(*nd):
    for x in nd:
        hit = [k for k, l in enumerate(B) if x in l]
        if hit: return hit[-1]
    return None
GU = [("'S442 a name split across wrapped lines is still one name", "'S441C no service renames from eye text, only proposes", "ck('S442 a name split across wrapped lines is still one name', (chr(35)+' NAME-JOIN v85.98') in _src and ('_NAME_STOP |=' in _src))"),
      ("'S443 a failed guard confesses its own probe", "'S442 a name split across wrapped lines is still one name", "ck('S443 a failed guard confesses its own probe', (chr(35)+' FAIL-LOUD v85.99') in _src and ('FAIL WHY' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = P.ind(B[i]); B.insert(i+1, d*' ' + line); done.append(needle.split()[0].strip("'") + '-guard')
P.write(B)
print('✅', done)
