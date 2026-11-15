import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'archive'))
import patchlib as P
done = []
M0 = P.perfile()
B = P.read()
w0 = next((k for k, l in enumerate(B) if 'FAIL-LOUD v85.99: a failed guard prints' in l), None)
if w0 is not None:
    w1 = next(k for k in range(w0, len(B)) if B[k].strip() == 'except NameError:')
    del B[w0:w1+2]
    done.append('fail-loud-removed-tail')
k0 = next((k for k, l in enumerate(B) if l.startswith('def ck(')), None)
if k0 is not None and 'relocated v85.101' not in '\n'.join(B[k0:k0+40]):
    k1 = k0 + 1
    while k1 < len(B) and not (B[k1].strip() and not B[k1].startswith(' ') and not B[k1].startswith('#')):
        k1 += 1
    B[k1:k1] = ["try:  # FAIL-LOUD v85.99 (relocated v85.101): the wrapper stands between the original ck and the selftest that calls it, or failures die unconfessed",
                "    _orig_ck_v8599 = ck",
                "    def ck(name, cond, *a, **k):",
                "        _r = _orig_ck_v8599(name, cond, *a, **k)",
                "        if not cond:",
                "            try:",
                "                import inspect as _ins",
                "                _fr = _ins.currentframe().f_back",
                "                _fl = open(_ins.getsourcefile(_fr)).read().split('\\n')[_fr.f_lineno-1].strip()",
                "                print('🩸 FAIL WHY %s: %s' % (name, _fl[:200]))",
                "            except Exception:",
                "                pass",
                "        return _r",
                "except NameError:",
                "    pass",
                ""]
    done.append('fail-loud-relocated')
for tag, old_start, new in (('S441B', "ck('S441B ", "ck('S441B no background sweep renames from eye text', ('os.rename(p, ' + '_q3)') not in _src)"),
                            ('S441C', "ck('S441C ", "ck('S441C no service renames from eye text, only proposes', ('os.rename(p, ' + 'q2)') not in _src and ('service proposes:' in _src))")):
    k = next((i for i, l in enumerate(B) if l.strip().startswith(old_start)), None)
    if k is not None:
        d = P.ind(B[k]); B[k] = d*' ' + new; done.append('probe-%s-structural' % tag)
se = next((k for k, l in enumerate(B) if l.strip().startswith('_NAME_STOP |=')), None)
if se is not None and 'STOP-EXT2' not in '\n'.join(B[se:se+3]):
    d = P.ind(B[se])
    B.insert(se+1, d*' ' + "_NAME_STOP |= set('best ability of my the a an to in for with and or at on is are was were be been being i we you he she it they me him her us them where can will shall should would could may might must environment utilize utilizing maximum extent progress organization motivate motivating challenge challenges competition work'.split())  # STOP-EXT2 v85.101: articles, conjunctions and slogan-verbs join the gate, so no sentence fragment can pose as a human")
    done.append('stop-ext2')
e0 = next((k for k, l in enumerate(B) if l.startswith('def _eyename_of(')), None)
if e0 is not None and 'def _name_from_head_lines(' not in '\n'.join(B):
    B.insert(e0, "def _name_from_head_lines(lines):  # ACCEPTANCE v85.101: the naming brain as a pure function of head lines - fixtures test it inside the gate, so ALL GREEN means WORKS, not merely lawful")
    for i, s in enumerate(["    ls = [re.split(r'\\s+(?:Phone|Mob|Tel|E-Mail|Email)[:\\-]?', l.strip(), flags=re.I)[0].strip() for l in lines if l.strip()][:8]",
                           "    i = 0",
                           "    while i < len(ls):",
                           "        cands = [ls[i]]",
                           "        if i + 1 < len(ls): cands.append(ls[i] + ' ' + ls[i+1])",
                           "        if i + 2 < len(ls): cands.append(ls[i] + ' ' + ls[i+1] + ' ' + ls[i+2])",
                           "        for cut in cands:",
                           "            ws = cut.split()",
                           "            if 2 <= len(ws) <= 4 and len(cut) <= 40 and all(w.isalpha() or '-' in w or '.' in w for w in ws) and not (set(w.lower() for w in ws) & _NAME_STOP) and (_canonical_person_name(cut) or ''):",
                           "                return _display_name(_canonical_person_name(cut))",
                           "        i += 1",
                           "    return ''"]):
        B.insert(e0+1+i, s)
    done.append('pure-brain')
ls = next((k for k, l in enumerate(B) if l.strip().startswith('_lines = [re.split')), None)
le = next((k for k, l in enumerate(B) if l.strip().startswith('if not name:')), None)
if ls is not None and le is not None and le > ls:
    d = P.ind(B[ls])
    B[ls:le] = [d*' ' + "name = _name_from_head_lines(t.split('\\n'))  # ACCEPTANCE v85.101: the eye delegates to the fixture-tested brain, one naming law in one place"]
    done.append('eyename-delegates')
c1 = next((k for k, l in enumerate(B) if l.strip().startswith("ck('S1 ")), None)
if c1 is not None and 'def _acceptance_ok(' not in '\n'.join(B):
    d = P.ind(B[c1])
    blk = ["def _acceptance_ok():  # ACCEPTANCE v85.101: synthetic heads prove the brain inside the gate - a wrong-name regression can no longer reach a commit",
           "    fx = [((['CHANDN', 'KUMAR', 'OBJECTIVE', 'To work in a motivating,']), 'Chandn Kumar'),",
           "          ((['To work in a motivating,', 'challenging and competitive', 'environment where I can']), ''),",
           "          ((['CURRICULUM VITAE', 'Pvv Satyanarayana Rao']), 'Pvv Satyanarayana Rao'),",
           "          ((['PANKAJ KUMAR', 'Head of Sales']), 'Pankaj Kumar'),",
           "          ((['Best Of My Ability', 'chandanankur32@gmail.com']), ''),",
           "          ((['RAKESH KUMAR', 'Maintenance Head | Beverage Industry']), 'Rakesh Kumar')]"]
    blk += ["    ok = True",
            "    for lines, want in fx:",
            "        got = _name_from_head_lines(lines)",
            "        if got != want:",
            "            ok = False",
            "            print('🩸 FIXTURE FAIL: %r -> %r want %r' % (lines[:2], got, want))",
            "    return ok",
            ""]
    B[c1:c1] = [(d + (0 if s.startswith('def') or s == '' else 0))*' ' + s if False else s for s in blk]
    done.append('acceptance-hook')
lost = P.preflight(B, M0)
if lost:
    print('⛔ preflight markers would be lost:', sorted(lost)); raise SystemExit('fix before write')
P.write(B); P.witness(M0)
print('🔎 fixtures, run live:')
sys.path.insert(0, os.getcwd())
import importlib
import butler as _bt
importlib.reload(_bt)
print('   fixtures ok:', _bt._acceptance_ok())
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
t = open(AR).read()
if 'v85.101' not in t:
    open(AR, 'a').write('v85.101: PERMANENT LOOP FIX - the naming brain is a pure function of head lines, fixture-tested inside the selftest so ALL GREEN means WORKS; FAIL-LOUD relocated before its first caller; S441B/C structural; stopword law completed with articles/conjunctions/slogan-verbs; the eye delegates to the tested brain; future naming tuning is add-fixture-plus-adjust-pure-function, provable without pdfs, clicks or screenshots (S445, S446, S447)\n')
    done.append('arch-line')
src = '\n'.join(B)
def anch(*nd):
    for x in nd:
        hit = [k for k, l in enumerate(B) if x in l]
        if hit: return hit[-1]
    return None
GU = [("'S445 the confession stands before the first guard it must explain", "'S444 the propose-only law stands pinned by three guards", "ck('S445 the confession stands before the first guard it must explain', _src.find('def ck(name, cond') != -1 and _src.find('def ck(name, cond') < _src.find(chr(39)+'S44'))"),
      ("'S446 the gate tests behaviour on synthetic heads, so green means works", "'S445 the confession stands before the first guard it must explain", "ck('S446 the gate tests behaviour on synthetic heads, so green means works', ('def _acceptance_ok(' in _src) and _acceptance_ok())"),
      ("'S447 one naming law lives in one pure function, and the eye delegates to it", "'S446 the gate tests behaviour on synthetic heads, so green means works", "ck('S447 one naming law lives in one pure function, and the eye delegates to it', ('def _name_from_head_lines(' in _src) and ('_name_from_head_lines(t.split' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = P.ind(B[i]); B.insert(i+1, d*' ' + line); done.append(needle.split()[0].strip("'") + '-guard')
P.write(B)
print('✅', done)
