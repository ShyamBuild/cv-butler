import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
for k, l in enumerate(g):
    if l.startswith('def _smart_input(') and 'ALWAYS-RAW v85.6' in l and '# ALWAYS-RAW' not in l:
        g[k] = l.replace('ALWAYS-RAW v85.6', '# ALWAYS-RAW v85.6')
        done.append('always-raw-hash'); break
srcg = '\n'.join(g)
if srcg != open(G).read():
    ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
snap = list(B)
w0 = next(k for k, l in enumerate(B) if l.startswith('def _chair_wa_text('))
w1 = next(k for k in range(w0 + 1, len(B)) if B[k].startswith('def '))
for k in range(w0, w1):
    if B[k].strip().startswith("if kind == 'refer':") and 'SCENARIO-REFER' in B[k]:
        d = ind(B[k])
        B[k:k+3] = [d*' ' + "if kind == 'refer':  # SCENARIO-REFER v85.4 (explicit v85.7): the master's courtesy is read and formatted here, with no helper standing between it and the candidate",
                    (d+4)*' ' + "try:",
                    (d+8)*' ' + "_rp = os.path.join(DRAFTS_DIR, 'refer.txt')",
                    (d+8)*' ' + "if os.path.exists(_rp): return open(_rp).read().strip().format_map(_draft_fields(name, _pos_of(p, _pl_root()), p))",
                    (d+4)*' ' + "except Exception:",
                    (d+8)*' ' + "pass"]
        done.append('refer-explicit'); break
print('🔎 DRAFTS_DIR =', next((l for l in B if l.startswith('DRAFTS_DIR =')), 'NOT FOUND AT TOP LEVEL'))
_rp = os.path.join(os.getcwd(), 'drafts', 'refer.txt')
print('🔎 drafts/refer.txt exists:', os.path.exists(_rp))
if os.path.exists(_rp):
    print('🔎 first line:', open(_rp).read().split('\n')[0])
print('🔎 _chair_wa_text region:')
for l in B[w0:w0+14]:
    print('   |', l)
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
M1 = set(markers(open('butler.py').read().split('\n'))) | set(markers(open(G).read().split('\n')))
M0 = set(markers(snap)) | set(markers(g))
lost = M0 - M1
if lost:
    print('⛔ witness diff:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff: 0 laws lost -', len(M0), 'before,', len(M1), 'after')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.7' not in t:
        open(AR, 'a').write('v85.7: every marker wears its own hash (standing rule); the refer courtesy is read and formatted explicitly in _chair_wa_text; ship prints DRAFTS_DIR, file existence and the composer region so blindness costs one receipt, not one lap\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S340 no state may downgrade the keyboard - the REPL always hears keys", "'S339 no guard may pin a read-call - prompts are law, readers are manners", "ck('S340 no state may downgrade the keyboard - the REPL always hears keys', (chr(35)+' ALWAYS-RAW v85.6') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and ('_seated' not in open(os.path.join(BASE_DIR, 'briefing.py')).read().split('def _smart_input(')[1].split(chr(10) + 'def ')[0]))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
