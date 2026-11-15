import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if l.strip().startswith("out = {'company': '', 'role': '', 'loc': '', 'designation': ''}"):
        B[k] = ind(l)*' ' + "out = {'company': '', 'role': '', 'loc': '', 'designation': '', 'client': ''}"
        done.append('client-key'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith('client = os.path.basename(os.path.dirname(pospath))') and "out['client']" not in '\n'.join(B[k:k+3]):
        B.insert(k+1, ind(l)*' ' + "out['client'] = client")
        done.append('client-read'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("if parts: say('🏢 ' + ' · '.join(parts))") and 'CLIENT-ASK' not in '\n'.join(B[k:k+3]):
        d = ind(l)
        B.insert(k+1, d*' ' + "if not i['company'] and (i['role'] or i['loc']):")
        B.insert(k+2, (d+4)*' ' + "say(f\"🏢 company unknown for client {i.get('client') or '?'} - teach once: client {i.get('client') or '?'} = <company>\")  # CLIENT-ASK v84.23: an ask must speak where the master is looking")
        done.append('client-ask'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if "'client', 'posmeta')" in l and 'missed' not in l:
        B[k] = l.replace("'client', 'posmeta')", "'client', 'posmeta', 'missed', 'jd', 'nudge', 'refer')")
        done.append('cli-keywords-tuple'); break
for k, l in enumerate(B):
    if l.strip().startswith("elif _v == 'posmeta':") and 'KEYWORDS-CLI' not in '\n'.join(B[k:k+4]):
        d = ind(l)
        B.insert(k+1, d*' ' + "elif _v in ('missed', 'jd', 'nudge', 'refer'):  # KEYWORDS-CLI v84.23: the keyword habit works in every door")
        B.insert(k+2, (d+4)*' ' + "import briefing as _br")
        B.insert(k+3, (d+4)*' ' + "_fn = getattr(_br, 'do_' + _v, None)")
        B.insert(k+4, (d+4)*' ' + "if _fn: _fn(' '.join(_a), _pl_root(), print)")
        B.insert(k+5, (d+4)*' ' + "else: print('🤷 voice missing: ' + _v)")
        done.append('keywords-cli'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S280 an untold company asks where the master is looking", "'S279 the roleline speaks designation, company, role and location in one clause", "ck('S280 an untold company asks where the master is looking', (chr(35)+' CLIENT-ASK v84.23') in _src)"),
      ("'S281 the keywords answer in the bare terminal too", "'S280 an untold company asks where the master is looking', ", "ck('S281 the keywords answer in the bare terminal too', (chr(35)+' KEYWORDS-CLI v84.23') in _src)")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
