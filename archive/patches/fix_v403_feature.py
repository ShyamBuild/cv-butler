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
W0 = open('wa.py').read()
w = W0.split('\n')
snapw = list(w)
i0 = next(k for k, l in enumerate(w) if l.startswith('def send_review('))
c0 = next((k for k in range(i0, i0+12) if w[k].strip().startswith("code = 'import sys, wa;")), None)
kif = next((k for k in range(i0, i0+20) if w[k].strip().startswith('if r != 0:')), None)
if c0 is not None and kif is not None and 'WA-STATUS' not in '\n'.join(w[i0:kif]):
    w[c0:kif] = ["    import subprocess, sys",
                 "    st = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.wa_status')  # WA-STATUS v85.31: the child reports ok / discard / fail in one word, so a deliberate discard never wears a failure's coat",
                 "    try:",
                 "        os.remove(st)",
                 "    except Exception:",
                 "        pass",
                 "    _lines = ['import sys, wa', '_seen = []', \"def _s(t='', *a, **k):\", '    _seen.append(str(t)); print(t)', 'r = wa._send_review_body(%r, %r, _s)' % (phone, text), \"st = 'ok'\", \"if any('whatsapp failed' in x for x in _seen): st = 'fail'\", \"elif any('discarded' in x for x in _seen): st = 'discard'\", \"open(%r, 'w').write(st)\" % st]",
                 "    code = '\\n'.join(_lines)",
                 "    rr = subprocess.call([sys.executable, '-c', code], cwd=os.path.dirname(os.path.abspath(__file__)))",
                 "    try:",
                 "        outcome = open(st).read().strip()",
                 "    except Exception:",
                 "        outcome = 'fail' if rr != 0 else 'ok'"]
    w[kif] = "    if outcome == 'fail' or rr != 0:  # WA-STATUS v85.31: only a true failure parks; discard and ok return in silence"
    done.append('status-protocol')
srcw = '\n'.join(w)
if srcw != W0:
    ast.parse(srcw); open('wa.py', 'w').write(srcw)
    print('🔎 wrapper region now:')
    L = open('wa.py').read().split('\n')
    j0 = next(k for k, l in enumerate(L) if l.startswith('def send_review('))
    for l in L[j0:j0+30]:
        print('   |', l)
B0 = open('butler.py').read()
B = B0.split('\n')
snap = list(B)
o0 = next(k for k, l in enumerate(B) if l.startswith('def outcome_cmd('))
o1 = next(k for k in range(o0 + 1, len(B)) if B[k].startswith('def '))
sd = next((k for k in range(o0, o1) if B[k].strip().startswith('wa.send_review(ph,')), None)
if sd is not None and '_wr = wa.send_review' not in B[sd]:
    B[sd] = B[sd].replace('wa.send_review(', '_wr = wa.send_review(', 1)
    done.append('wr-captured')
tk = next((k for k in range(o0, o1) if B[k].strip().startswith("if _k == 't': pass")), None)
if tk is not None and '_wr = True' not in '\n'.join(B[o0:tk]):
    B.insert(tk, ind(B[tk])*' ' + "_wr = True  # DEED-TRUTH v85.31: the deed line reports what the window actually did - drafted, parked, or internal")
    done.append('wr-default')
dl = next((k for k in range(o0, o1) if 'CINE-LINE v85.1' in B[k] and '📱 drafted' in B[k]), None)
if dl is not None and '_wr' not in B[dl]:
    B[dl] = B[dl].replace("('📱 drafted' if (_k != 't' and draft) else ('no 📱' if draft else 'internal · no 📱'))",
                          "('📱 drafted' if (_k != 't' and draft and _wr) else ('📱 parked' if (_k != 't' and draft and not _wr) else ('no 📱' if draft else 'internal · no 📱')))")
    done.append('deed-truth')
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
    if 'v85.31' not in t:
        open(AR, 'a').write('v85.31: WA-STATUS in plain constructs (full try blocks, child code joined from a list of strings) - the child writes ok/discard/fail and only a true failure parks; DEED-TRUTH - the deed line says parked when the draft parked, drafted only when the ritual completed (S369, S370)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S369 a deliberate discard never wears a failure's coat", "'S368 playwright is started once per process and shared by every door", "ck('S369 a deliberate discard never wears a failure'+chr(39)+'s coat', (chr(35)+' WA-STATUS v85.31') in open(os.path.join(BASE_DIR, 'wa.py')).read())"),
      ("'S370 the deed line reports what the window actually did", "'S369 a deliberate discard never wears a failure's coat", "ck('S370 the deed line reports what the window actually did', (chr(39)+'📱 parked'+chr(39)) in _src and ('_wr = wa.send_review' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
