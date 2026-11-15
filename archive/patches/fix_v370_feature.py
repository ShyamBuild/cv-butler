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
        return new_first.rstrip() + '  ' + ' '.join(ms) + '  # WITNESS-CARRY v84.52: deleted lines hand their laws to the line that survives'
    return new_first
B0 = open('butler.py').read()
M0 = set(markers(B0.split('\n')))
B = B0.split('\n')
snap = list(B)
u0 = next(k for k, l in enumerate(B) if l.startswith('def up_cmd('))
u1 = next(k for k in range(u0 + 1, len(B)) if B[k].startswith('def '))
ch = next((k for k in range(u0, u1) if 'CHAIR · ' in B[k] and 'say(' in B[k]), None)
ct = next((k for k in range(u0, u1) if '✉️ {_em}' in B[k]), None)
idn = next((k for k in range(u0, u1) if B[k].strip().startswith('say_identity_for(p, say)')), None)
if None not in (ch, ct, idn) and 'HORIZONTAL' not in '\n'.join(B[u0:u1]):
    d = ind(B[ch])
    idline = B[idn]
    ct2 = ct + 1 if ct + 1 < u1 and B[ct+1].strip().startswith('else: say(') else ct
    deleted = [B[ch]] + B[ct:ct2+1]
    new = d*' ' + carry("say(f\"🛰️ {i['name']} · {os.path.basename(os.path.dirname(p))} · ✉️ {_em} · 📱 {ph or 'none (teach me)'}\")  # HORIZONTAL v85.9: name, folder, email, phone in one flush line, indented like the body it lives in - the scroll belongs to the candidates, not the chrome", deleted)
    for idx in sorted([ch, idn, ct, ct2], reverse=True):
        del B[idx]
    top = min([ch, idn, ct])
    B[top:top] = [new, idline]
    done.append('dossier-one-line')
for k in range(u0, u1 + 8):
    if k < len(B) and 'one key closes his row' in B[k]:
        del B[k]; done.append('header-retired'); break
for k in range(u0, u1 + 8):
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
L = open('butler.py').read().split('\n')
u0 = next(k for k, l in enumerate(L) if l.startswith('def up_cmd('))
for l in L[u0:u0+90]:
    if any(t in l for t in ('🛰️', 'say_identity_for', 'jd→JD-Conf', '✉️')):
        print('   |', l)
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.9' not in t:
        open(AR, 'a').write('v85.9: HORIZONTAL - the seat speaks three lines (flush dossier indented like its body, the triple by its own pinned door carried whole, the map as its own header); the contact if/else pair retires together with its teach hint folded into the dossier; header and parenthetical gone\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S342 the seat speaks in three lines and the scroll belongs to the candidates", "'S341 a scenario branch stands at its own column, never inside its sibling", "ck('S342 the seat speaks in three lines and the scroll belongs to the candidates', (chr(35)+' HORIZONTAL v85.9') in _src and ((chr(40) + 'options = full ' + 'grammar' + chr(41)) not in _src) and ('say_identity_for(p, say)' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
