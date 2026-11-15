import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'archive'))
import patchlib as P
done = []
M0 = P.perfile()
B = P.read()
w0 = next((k for k, l in enumerate(B) if 'FAIL-LOUD v85.99: a failed guard prints' in l), None)
if w0 is not None:
    w1 = w0
    while w1 < len(B) and not B[w1].strip() == 'pass':
        w1 += 1
    del B[w0:w1+1]
    done.append('fail-loud-removed-tail')
k0 = next((k for k, l in enumerate(B) if l.startswith('def ck(')), None)
if k0 is not None and 'FAIL-LOUD v85.99 (relocated v85.101)' not in '\n'.join(B[k0:k0+40]):
    k1 = k0 + 1
    while k1 < len(B) and not (B[k1].strip() and not B[k1].startswith(' ') and not B[k1].startswith('#')):
        k1 += 1
    B[k1:k1] = ["try:  # FAIL-LOUD v85.99 (relocated v85.101): the wrapper must stand between the original ck and the selftest that calls it, or failures die unconfessed",
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
lost = P.preflight(B, M0)
if lost:
    print('⛔ preflight markers would be lost:', sorted(lost)); raise SystemExit('fix before write')
P.write(B); P.witness(M0)
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
t = open(AR).read()
if 'v85.101' not in t:
    open(AR, 'a').write('v85.101: FAIL-LOUD relocated between the original ck and its first caller so every future FAIL prints its own probe; S441B/C repinned structurally on the absence of the eye-rename calls themselves, spelled by concatenation; the borrowed-number debt is diagnosed (taught store keys by stem alone, email computed but never used for identity) and deferred to a consented schema lap (S445)\n')
    done.append('arch-line')
src = '\n'.join(B)
def anch(*nd):
    for x in nd:
        hit = [k for k, l in enumerate(B) if x in l]
        if hit: return hit[-1]
    return None
GU = [("'S445 the confession stands before the first guard it must explain", "'S444 the propose-only law stands pinned by three guards", "ck('S445 the confession stands before the first guard it must explain', _src.find('def ck(name, cond') != -1 and _src.find('def ck(name, cond') < _src.find(chr(39)+'S44'))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = P.ind(B[i]); B.insert(i+1, d*' ' + line); done.append(needle.split()[0].strip("'") + '-guard')
P.write(B)
print('✅', done)
