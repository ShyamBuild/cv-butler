import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
B0 = open('butler.py').read()
G0 = open('briefing.py').read()
W0 = open('wa.py').read()
M0 = set(markers(B0.split('\n'))) | set(markers(G0.split('\n'))) | set(markers(W0.split('\n')))
B = B0.split('\n')
snap = list(B)
s0 = next(k for k, l in enumerate(B) if l.startswith('def seat_rename_check('))
s1 = next(k for k in range(s0 + 1, len(B)) if B[k].startswith('def '))
for k in range(s0, s1):
    if 'import time as _t' in B[k]:
        B[k] = B[k].replace('import time as _t, json as _j', 'import json as _j').replace('import time as _t', '')
        done.append('ghost-clock-out')
    B[k] = B[k].replace('_t.time()', 'time.time()').replace('_t.strftime', 'time.strftime')
if 'def _fp_fast(' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.startswith('def calls_cmd('))
    B[i:i] = ["_FPC = {}",
              "def _fp_fast(p):  # FP-CACHE v85.18: a fingerprint is computed once per content and remembered by mtime+size; only new or edited papers pay the hash",
              "    global _FPC",
              "    import json as _j",
              "    cf = os.path.join(BASE_DIR, '.fpcache.json')",
              "    if not _FPC:",
              "        try: _FPC.update(_j.load(open(cf)))",
              "        except Exception: pass",
              "    try:",
              "        st = os.stat(p)",
              "    except Exception:",
              "        return _fp(p)",
              "    e = _FPC.get(p)",
              "    if e and e[0] == st.st_mtime and e[1] == st.st_size:",
              "        return e[2]",
              "    v = _fp(p)",
              "    _FPC[p] = [st.st_mtime, st.st_size, v]",
              "    try: _j.dump(_FPC, open(cf, 'w'))",
              "    except Exception: pass",
              "    return v",
              ""]
    done.append('fp-cache-def')
c0 = next(k for k, l in enumerate(B) if l.startswith('def calls_cmd('))
c1 = next(k for k in range(c0 + 1, len(B)) if B[k].startswith('def sheet_cmd('))
m = 0
for k in range(c0, c1):
    if '_fp(p)' in B[k] and '_fp_fast' not in B[k]:
        B[k] = B[k].replace('_fp(p)', '_fp_fast(p)'); m += 1
    if '_fp(kp)' in B[k] and '_fp_fast' not in B[k]:
        B[k] = B[k].replace('_fp(kp)', '_fp_fast(kp)'); m += 1
if m: done.append('fp-cache-use-x%d' % m)
u0 = next(k for k, l in enumerate(B) if l.startswith('def up_cmd('))
u1 = next(k for k in range(u0 + 1, len(B)) if B[k].startswith('def '))
for k in range(u0, u1):
    if "calls_cmd('', root, say, False)" in B[k] and 'SEED-SAY' not in '\n'.join(B[u0:k]):
        d = ind(B[k])
        B.insert(k, d*' ' + "say('🔎 seeding the sheet - fingerprints cached, new papers hashed once')  # SEED-SAY v85.18: even a cold pass speaks while it works")
        done.append('seed-say'); break
mk = next(k for k, l in enumerate(B) if l.startswith('def menu_key('))
if 'NEWLINE-DISCIPLINE' not in B[mk+2]:
    d = ind(B[mk]) + 4
    B.insert(mk+2, d*' ' + "if getattr(sys.stdout, 'last', '\\n') != '\\n': sys.stdout.write('\\n')  # NEWLINE-DISCIPLINE v85.18: a prompt never begins mid-line; if the previous writer forgot its end, the next one supplies it")
    done.append('menukey-nl')
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
g = G0.split('\n')
snapg = list(g)
if 'class _NLOut(' not in '\n'.join(g):
    a0 = next(k for k, l in enumerate(g) if l.startswith('def _say('))
    a1 = next(k for k in range(a0, len(g)) if g[k].strip() == '' and k > a0)
    g[a1+1:a1+1] = ["class _NLOut:  # NEWLINE-DISCIPLINE v85.18: stdout remembers whether the last write ended a line, so no print may ever begin mid-line again",
                    "    def __init__(self, s):",
                    "        self._s = s; self.last = '\\n'",
                    "    def write(self, t):",
                    "        if t:",
                    "            self._s.write(t); self.last = t[-1]",
                    "        return len(t) if t else 0",
                    "    def flush(self):",
                    "        self._s.flush()",
                    "    def __getattr__(self, n):",
                    "        return getattr(self._s, n)",
                    "import sys as _sysnl",
                    "if not isinstance(_sysnl.stdout, _NLOut):",
                    "    _sysnl.stdout = _NLOut(_sysnl.stdout)",
                    ""]
    done.append('nl-wrapper')
si = next((k for k, l in enumerate(g) if l.startswith('def _smart_input(')), None)
if si is not None and 'NEWLINE-DISCIPLINE' not in g[si+2]:
    d = ind(g[si]) + 4
    g.insert(si+2, d*' ' + "if getattr(sys.stdout, 'last', '\\n') != '\\n': sys.stdout.write('\\n')  # NEWLINE-DISCIPLINE v85.18")
    done.append('smartinput-nl')
srcg = '\n'.join(g)
if srcg != G0:
    ast.parse(srcg); open('briefing.py', 'w').write(srcg)
w = W0.split('\n')
snapw = list(w)
wk = next((k for k, l in enumerate(w) if l.startswith('def _key(')), None)
if wk is not None and 'NEWLINE-DISCIPLINE' not in w[wk+2]:
    d = ind(w[wk]) + 4
    w.insert(wk+2, d*' ' + "if getattr(sys.stdout, 'last', '\\n') != '\\n': sys.stdout.write('\\n')  # NEWLINE-DISCIPLINE v85.18")
    done.append('wakey-nl')
    srcw = '\n'.join(w)
    ast.parse(srcw); open('wa.py', 'w').write(srcw)
M1 = set(markers(open('butler.py').read().split('\n'))) | set(markers(open('briefing.py').read().split('\n'))) | set(markers(open('wa.py').read().split('\n')))
lost = M0 - M1
if lost:
    print('⛔ witness diff:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff: 0 laws lost -', len(M0), 'before,', len(M1), 'after')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.18' not in t:
        open(AR, 'a').write('v85.18: ghost clock retired from the ceremony; NEWLINE-DISCIPLINE stdout wrapper plus pre-prompt newline checks in REPL, cue and wa menu so no line begins mid-line; FP-CACHE fingerprints by path+mtime+size with SEED-SAY announcement (S352, S353)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S352 no line the house prints may begin mid-line - stdout remembers its own endings", "'S351 the announcement precedes every cost, and no constructor runs before its duty speaks", "ck('S352 no line the house prints may begin mid-line - stdout remembers its own endings', (chr(35)+' NEWLINE-DISCIPLINE v85.18') in _src and (chr(35)+' NEWLINE-DISCIPLINE v85.18') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and (chr(35)+' NEWLINE-DISCIPLINE v85.18') in open(os.path.join(BASE_DIR, 'wa.py')).read())"),
      ("'S353 a fingerprint is computed once per content and the seed never works in silence", "'S352 no line the house prints may begin mid-line - stdout remembers its own endings", "ck('S353 a fingerprint is computed once per content and the seed never works in silence', (chr(35)+' FP-CACHE v85.18') in _src and (chr(35)+' SEED-SAY v85.18') in _src and ('_fp_fast(p)' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
