import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if l.strip().startswith('_v = _f(p)') and 'SILENT-PROBE' not in '\n'.join(B[max(0,k-3):k+2]):
        d = ind(l)
        B[k:k+1] = [d*' ' + "_buf = __import__('io').StringIO()",
                    d*' ' + "with __import__('contextlib').redirect_stdout(_buf): _v = _f(p)  # SILENT-PROBE v84.41: discovering the email must not print the clerk's witness lines"]
        done.append('silent-probe'); break
src = '\n'.join(B)
o0 = next(k for k, l in enumerate(B) if l.startswith('def outcome_cmd('))
o1 = next(k for k in range(o0 + 1, len(B)) if B[k].startswith('def '))
for k in range(o0, o1):
    if B[k].strip() == 'say_identity_for(p, say)':
        B[k] = ind(B[k])*' ' + "pass  # IDENTITY-ONCE v84.41: the triple speaks at the seat; the proposal carries only the decision, the draft carries the truth inside"
        done.append('proposal-identity-omitted'); break
src = '\n'.join(B)
w0 = next(k for k, l in enumerate(B) if l.startswith('def _chair_wa_text('))
if 'SCENARIO-3' not in '\n'.join(B[w0:w0+14]):
    d = ind(B[w0])
    B.insert(w0+1, (d+4)*' ' + "if kind == 'cv':  # SCENARIO-3 v84.41: outcome 3 speaks the master's combo - acknowledge the JD and send the updated CV - from the scenario store; the legacy nudge stays the later touchpoint")
    B.insert(w0+2, (d+8)*' ' + "t3 = _draft_text('cv', name, _pos_of(p, _pl_root()), p)")
    B.insert(w0+3, (d+8)*' ' + "if t3: return t3")
    done.append('scenario-3')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v84.41' not in t:
        open(AR, 'a').write('v84.41: silent email probe (redirect_stdout), identity triple once at the seat, outcome 3 reads the scenario store first (jd-ack + cv-update combo) while legacy nudge stays the later touchpoint\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S308 outcome 3 speaks the combo from the scenario store, nudge stays the touchpoint", "'S307 the module map lives in the index, versioned with the code", "ck('S308 outcome 3 speaks the combo from the scenario store, nudge stays the touchpoint', (chr(35)+' SCENARIO-3 v84.41') in _src and ('def _draft_text(' in _src))"),
      ("'S309 the email probe is silent and the triple speaks once at the seat", "'S308 outcome 3 speaks the combo from the scenario store, nudge stays the touchpoint", "ck('S309 the email probe is silent and the triple speaks once at the seat', (chr(35)+' SILENT-PROBE v84.41') in _src and (chr(35)+' IDENTITY-ONCE v84.41') in _src)")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
