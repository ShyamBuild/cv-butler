import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
def carry(new_first, deleted):
    ms = markers(deleted)
    if ms:
        return new_first.rstrip() + '  ' + ' '.join(ms) + '  # WITNESS-CARRY v84.52'
    return new_first
B0 = open('butler.py').read()
M0 = set(markers(B0.split('\n')))
B = B0.split('\n')
snap = list(B)
u0 = next(k for k, l in enumerate(B) if l.startswith('def up_cmd('))
u1 = next(k for k in range(u0 + 1, len(B)) if B[k].startswith('def '))
ch = next((k for k in range(u0, u1) if 'CHAIR · ' in B[k] and B[k].strip().startswith('say(')), None)
ct = next((k for k in range(u0, u1) if '✉️ {_em}' in B[k] and B[k].strip().startswith('say(')), None)
hd = next((k for k in range(u0, u1) if 'one key closes his row' in B[k]), None)
op = next((k for k in range(u0, u1) if '(options = full grammar)' in B[k]), None)
if ch is not None and ct is not None:
    deleted = [B[ch], B[ct]]
    new = "say(f\"🛰️ {i['name']} · {os.path.basename(os.path.dirname(p))} · ✉️ {_em} · 📱 {ph or 'none'}\")  # HORIZONTAL v85.9: name, folder, email, phone in one flush line - the scroll belongs to the candidates, not to the chrome"
    lo, hi = min(ch, ct), max(ch, ct)
    B[lo:hi+1] = [new if lo == ch else carry(new, deleted)] if False else [carry(new, deleted)]
    done.append('dossier-one-line')
for k in range(u0, u1 + 6):
    if k < len(B) and 'one key closes his row' in B[k]:
        del B[k]; done.append('header-retired'); break
for k in range(u0, u1 + 6):
    if k < len(B) and '(options = full grammar)' in B[k]:
        del B[k]; done.append('paren-retired'); break
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
M1 = set(markers(open('butler.py').read().split('\n')))
lost = M0 - M1
if lost:
    print('⛔ witness diff:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff: 0 laws lost -', len(M0), 'before,', len(M1), 'after')
print('🔎 seat block now:')
u0 = next(k for k, l in enumerate(open('butler.py').read().split('\n')) if l.startswith('def up_cmd('))
for l in open('butler.py').read().split('\n')[u0:u0+40]:
    if any(t in l for t in ('🛰️', '🏢', 'jd→JD-Conf', 'say_identity_for')):
        print('   |', l)
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.9' not in t:
        open(AR, 'a').write('v85.9: HORIZONTAL - the seat speaks three lines (dossier flush at column zero, the triple by its own pinned door, the map as its own header); the one-key header and the options parenthetical retire; scroll belongs to candidates, not chrome\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S342 the seat speaks in three lines and the scroll belongs to the candidates", "'S341 a scenario branch stands at its own column, never inside its sibling", "ck('S342 the seat speaks in three lines and the scroll belongs to the candidates', (chr(35)+' HORIZONTAL v85.9') in _src and ((chr(40) + 'options = full ' + 'grammar' + chr(41)) not in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
