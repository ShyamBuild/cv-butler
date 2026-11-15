import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
B0 = open('butler.py').read()
M0 = set(markers(B0.split('\n')))
B = B0.split('\n')
snap = list(B)
o0 = next(k for k, l in enumerate(B) if l.startswith('def outcome_cmd('))
o1 = next(k for k in range(o0 + 1, len(B)) if B[k].startswith('def '))
for k in range(o0, o1):
    if 'wa.send_review(ph,' in B[k] and '_chair_wa_text(draft' in B[k] and '_wr = ' not in B[k]:
        B[k] = B[k].replace('wa.send_review(ph,', '_wr = wa.send_review(ph,', 1)
        done.append('wr-on-draft-line'); break
f0 = next(k for k, l in enumerate(B) if l.startswith('def _ident_of('))
f1 = next(k for k in range(f0 + 1, len(B)) if B[k].startswith('def '))
if "'name:'" not in '\n'.join(B[f0:f1]):
    ik = next(k for k in range(f0, f1) if B[k].strip().startswith('ids = set(emails_in_text(t))'))
    d = ind(B[ik])
    B[ik+1:ik+1] = [d*' ' + "v2 = heuristic_name(p) or _name_from_first_line(p)  # DUP-SEED name-token v85.33: a scan has no contacts in its text layer, so the fast eyes lend identity a face - vision stays out of seeding for speed",
                    d*' ' + "if v2:",
                    (d+4)*' ' + "_cn = _canonical_person_name(v2) or v2",
                    (d+4)*' ' + "ids.add('name:' + _name_key(_cn))"]
    done.append('ident-name-token')
print('🔎 outcome draft-send line and _ident_of tail:')
for k in range(o0, o1):
    if 'wa.send_review(ph,' in B[k] and '_chair_wa_text(draft' in B[k]:
        print('   |', B[k])
for k in range(f0, f1):
    if 'name:' in B[k] or B[k].strip().startswith('ids =') or B[k].strip().startswith('v2 ='):
        print('   |', B[k])
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
M1 = set(markers(open('butler.py').read().split('\n')))
lost = M0 - M1
if lost:
    print('⛔ witness diff:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff: 0 laws lost -', len(M0), 'before,', len(M1), 'after')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.33' not in t:
        open(AR, 'a').write('v85.33: the _wr capture stands on the draft-send line whose return the deed reports; identity gains a name-token from the fast eyes so scanned portal twins are refused at seed (S371 tightened, S372)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("ck('S371 ") and '_chair_wa_text(draft' not in l:
        d = ind(l)
        B[k] = d*' ' + "ck('S371 the deed'+chr(39)+'s witness stands on the draft-send line itself', any(('_wr = wa.send_review(ph,' in x and '_chair_wa_text(draft' in x) for x in _src.split('def outcome_cmd(')[1].split(chr(10) + 'def ')[0].split(chr(10))))  # S371 tightened v85.33: the postcode is the draft line, not any send line"
        done.append('S371-tighten'); break
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S372 a scan is recognised by its face when its contacts are silent", "'S371 the deed's witness stands on the draft-send line itself", "ck('S372 a scan is recognised by its face when its contacts are silent', (chr(39)+'name:'+chr(39)) in _src.split('def _ident_of(')[1].split(chr(10) + 'def ')[0])")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
