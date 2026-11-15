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
hz = next((k for k in range(u0, u1) if 'HORIZONTAL v85.9' in B[k]), None)
ch = next((k for k in range(u0, u1) if 'CHAIR · ' in B[k] and 'say(' in B[k] and 'HORIZONTAL' not in B[k]), None)
ct = next((k for k in range(u0, u1) if '✉️ {_em}' in B[k] and 'HORIZONTAL' not in B[k]), None)
idn = next((k for k in range(u0, u1) if B[k].strip().startswith('say_identity_for(p, say)')), None)
em = next((k for k in range(u0, u1) if B[k].strip().startswith("_em = ''")), None)
if hz is not None and em is not None and hz < em:
    d = ind(B[hz])
    idline = B[idn] if idn is not None else None
    ct2 = ct + 1 if ct is not None and ct + 1 < u1 and B[ct+1].strip().startswith('else: say(') else ct
    deleted = [B[hz]] + ([B[ch]] if ch is not None else []) + (B[ct:ct2+1] if ct is not None else [])
    new = d*' ' + carry("say(f\"🛰️ {i['name']} · {os.path.basename(os.path.dirname(p))} · ✉️ {_em} · 📱 {ph or 'none (teach me)'}\")  # HORIZONTAL v85.9 (re-seated v85.10): the dossier stands AFTER the block that births _em and ph - no variable answers before its birth", deleted)
    for idx in sorted([x for x in (hz, ch, idn, ct, ct2) if x is not None], reverse=True):
        del B[idx]
    anchor = next(k for k in range(u0, u1) if B[k].strip().startswith('say(') and 'jd→JD-Conf' in B[k])
    ins = [new] + ([idline] if idline else [])
    B[anchor:anchor] = ins
    done.append('dossier-reseated')
for k, l in enumerate(B):
    if 'call sheet seeded:' in l and ("'   📞" in l or '"   📞' in l or "f'   📞" in l):
        B[k] = l.replace("'   📞", "'📞").replace('"   📞', '"📞')
        done.append('seeded-flush'); break
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
    if any(t in l for t in ('🛰️', 'say_identity_for', 'jd→JD-Conf', "_em = ''")):
        print('   |', l)
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.10' not in t:
        open(AR, 'a').write('v85.10: the merged dossier is re-seated after the block that births _em and ph (birth-order in the seat, S343); the seeded census line loses its inherited leading spaces so the page aligns flush\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S343 in the seat no variable answers before its birth", "'S342 the seat speaks in three lines and the scroll belongs to the candidates", "ck('S343 in the seat no variable answers before its birth', (lambda seg: seg.find(chr(35)+' HORIZONTAL v85.9') > seg.find(\"_em = ''\") >= 0)(_src.split('def up_cmd(')[1].split('def covered_load(')[0]))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
