import ast, os, re, sys
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
h0 = next(k for k, l in enumerate(B) if l.startswith('def _draft_local_text('))
h1 = next(k for k in range(h0 + 1, len(B)) if B[k].startswith('def '))
fk = next((k for k in range(h0, h1) if B[k].strip().startswith("_fld = _cc.defaultdict(str,")), None)
if fk is not None and "'full': name" not in B[fk]:
    d = ind(B[fk])
    B[fk] = d*' ' + "_fld = _cc.defaultdict(str, {'name': name, 'full': name, 'position': _pi.get('role') or os.path.basename(os.path.dirname(p)), 'role': _pi.get('role') or os.path.basename(os.path.dirname(p)), 'roleline': _pi.get('role') or os.path.basename(os.path.dirname(p)), 'company': _pi.get('company') or _dm.get('company') or '', 'location': _pi.get('loc') or _pi.get('location') or ''})  # PLACEHOLDER-DIALECT v85.44: the door speaks the master's files' dialect - full, role and roleline arrive dressed, so no courtesy renders an empty name or a blank role"
    done.append('placeholder-dialect')
print('🔎 helper field line:')
for k in range(h0, h1):
    if '_fld = ' in B[k]:
        print('   |', B[k].strip()[:200])
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
    if 'v85.44' not in t:
        open(AR, 'a').write('v85.44: PLACEHOLDER-DIALECT - the one door offers full/role/roleline aliases beside name/position/company/location so every existing drafts file renders whole; defaultdict still catches keys the master invents tomorrow (S384)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S384 the door speaks the master's files' dialect - no courtesy renders an empty name", "'S383 a stumbling command confesses and the chat stays open", "ck('S384 the door speaks the master'+chr(39)+'s files'+chr(39)+' dialect - no courtesy renders an empty name', (chr(39)+'full'+chr(39)+': name') in _src and (chr(35)+' PLACEHOLDER-DIALECT v85.44') in _src)")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
