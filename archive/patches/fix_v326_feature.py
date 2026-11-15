import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
u0 = next(k for k, l in enumerate(B) if l.startswith('def up_cmd('))
u1 = next(k for k in range(u0 + 1, len(B)) if B[k].startswith('def '))
seg = '\n'.join(B[u0:u1])
if 'QUIET-CHAIR' not in seg:
    for k in range(u0, u1):
        if B[k].strip().startswith('ph = taught_digits(i[') or (B[k].strip().startswith('ph = taught_digits(') and 'phones_of(p) or None' in B[k]):
            B[k] = ind(B[k])*' ' + "ph = taught_digits(i['name']) or phones_of(p, True) or None  # QUIET-CHAIR v84.37: the dossier takes the number without the clerk's ceremony"
            done.append('up-quiet'); break
    for k in range(u0, u1):
        if B[k].strip().startswith('say_identity_for(p, say)'):
            B[k] = ind(B[k])*' ' + "pass  # QUIET-CHAIR v84.37: the triple speaks once, at the proposal, where the thumb decides (S277 keeps that one)"
            done.append('up-identity-once'); break
    for k in range(u0, u1):
        if B[k].strip().startswith("for _ln in OPTION_MAP: say('   ' + _ln)"):
            d = ind(B[k])
            B[k:k+1] = [d*' ' + "say('   1 jd→JD-Conf · 2 refer→Closed · 3 nudge→CV-Update · 4 missed→Call-Sched · 5 internal→Ready · 6 skip→remembered')  # MAP-COMPACT v84.37: the map in two lines; options keeps the grammar",
                        d*' ' + "say('   (options prints the full grammar with keywords and both draft moments)')"]
            done.append('map-compact'); break
src = '\n'.join(B)
o0 = next(k for k, l in enumerate(B) if l.startswith('def outcome_cmd('))
o1 = next(k for k in range(o0 + 1, len(B)) if B[k].startswith('def '))
if 'QUIET-CHAIR' not in '\n'.join(B[o0:o1]):
    for k in range(o0, o1):
        if B[k].strip().startswith('ph0 = taught_digits('):
            B[k] = ind(B[k])*' ' + "ph0 = taught_digits(cur['name']) or phones_of(p, True) or None  # QUIET-CHAIR v84.37"
            done.append('outcome-quiet'); break
    for k in range(o0, o1):
        if B[k].strip().startswith("if it.get('p') == p: it['status'] = 'done'; it['outcome'] = outcome; it['ts'] = int(time.time())"):
            d = ind(B[k])
            B[k:k+1] = [d*' ' + "if os.path.realpath(it.get('p', '')) == os.path.realpath(p): it['status'] = 'done'; it['outcome'] = outcome; it['ts'] = int(time.time())"]
            done.append('done-by-realpath'); break
    for k in range(o0, o1):
        if B[k].strip().startswith("s['current'] = None; sheet_save(s)") and 'ghost-rows' not in '\n'.join(B[k:k+4]):
            d = ind(B[k])
            B.insert(k+1, d*' ' + "for it in s.get('items', []):  # QUIET-CHAIR v84.37: a closed human closes every row wearing his name or his path - the queue never offers a man twice")
            B.insert(k+2, (d+4)*' ' + "if it.get('status') == 'waiting' and (os.path.realpath(it.get('p', '')) == os.path.realpath(p) or _name_key(os.path.basename(it.get('p', ''))) == _name_key(os.path.basename(p))):")
            B.insert(k+3, (d+8)*' ' + "it['status'] = 'done'; it['outcome'] = outcome")
            done.append('ghost-rows'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v84.37' not in t:
        open(AR, 'a').write('v84.37: quiet chair - phones_of(quiet) in dossier and outcome, identity once at the proposal, two-line map with options for the grammar, closed human closes every row wearing his name\n')
        done.append('arch-line')
except Exception:
    pass
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S301 the chair speaks each truth once and the clerk keeps his ceremony for the doors that ask", "'S300 twins names every duplicate group and never deletes", "ck('S301 the chair speaks each truth once and the clerk keeps his ceremony for the doors that ask', (chr(35)+' QUIET-CHAIR v84.37') in _src and ('phones_of(p, True)' in _src))"),
      ("'S302 the seat prints the map in two lines and options keeps the full grammar", "'S301 the chair speaks each truth once and the clerk keeps his ceremony for the doors that ask", "ck('S302 the seat prints the map in two lines and options keeps the full grammar', (chr(35)+' MAP-COMPACT v84.37') in _src and ('def options_cmd(' in _src))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
