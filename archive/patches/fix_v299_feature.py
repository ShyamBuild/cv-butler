import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def _pos_of(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def _draft_fields('))
    B[i:i] = ["def _pos_of(p, root):  # POS-OF v84.18: the position is the chair the paper lies under, else the client's child - never the list or stage folder above the paper",
              "    d = desk_load()",
              "    for chair in (d.get('primary'), d.get('secondary')):",
              "        if chair and p.startswith(chair + os.sep): return os.path.basename(chair)",
              "    rel = os.path.relpath(p, root).split(os.sep)",
              "    return rel[1] if len(rel) > 2 else (rel[0] if len(rel) > 1 else '')",
              ""]
    done.append('pos-of')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith('parts = os.path.relpath(p, root).split(os.sep)') and 'pos = parts[-2]' in '\n'.join(B[k:k+2]):
        d = ind(l)
        B[k:k+2] = [d*' ' + "pos = _pos_of(p, root)"]
        done.append('outcome-pos'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith('parts = p.split(os.sep)') and 'pos = parts[-2]' in '\n'.join(B[k:k+2]):
        d = ind(l)
        B[k:k+2] = [d*' ' + "pos = _pos_of(p, _pl_root())"]
        done.append('chase-pos'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("return collections.defaultdict(str, {'first':") and 'roleline' not in '\n'.join(B[max(0,k-4):k]):
        d = ind(l)
        B[k:k] = [d*' ' + "    _rl = []",
                  d*' ' + "    if role.strip(): _rl.append('the role of ' + role.strip())",
                  d*' ' + "    if meta.get('company'): _rl.append('in ' + meta['company'])",
                  d*' ' + "    if loc.strip(): _rl.append('for ' + loc.strip() + ' location')",
                  d*' ' + "    roleline = ' '.join(_rl) or 'the role we discussed'  # ROLELINE v84.18: the sentence omits what was never taught"]
        B[k+5] = B[k+5].replace("'signature': _sig()})", "'signature': _sig(), 'roleline': roleline})")
        done.append('roleline'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
DD = os.path.expanduser('~/CV_Tool/drafts')
OLD = {
 'refer.txt': "Hi {full}, thank you for your time today. I have noted you are not keen on the role of {role} in {company} for {loc} location - if any friend or colleague might fit, do refer them to me. I have shared the JD on email for your reference. Wishing you the very best.\n{signature}",
 'jd.txt': "Hi {full}, great speaking with you today. I have shared the JD for the role of {role} in {company} for {loc} location on your email - please go through it and confirm your interest so I can move your profile forward.\n{signature}",
 'cv.txt': "Hi {full}, as discussed on call, please share your updated CV at the earliest so I can push your profile to the manager today for the role of {role} in {company}.\n{signature}",
 'missed.txt': "Hi {full}, I tried reaching you just now about your application for the role of {role} in {company} - whenever you are free, please call me back or tell me a good time to connect.\n{signature}",
}
NEW = {
 'refer.txt': "Hi {full}, thank you for your time today. I have noted you are not keen on {roleline} - if any friend or colleague might fit, do refer them to me. I have shared the JD on email for your reference. Wishing you the very best.\n{signature}",
 'jd.txt': "Hi {full}, great speaking with you today. I have shared the JD for {roleline} on your email - please go through it and confirm your interest so I can move your profile forward.\n{signature}",
 'cv.txt': "Hi {full}, as discussed on call, please share your updated CV at the earliest so I can push your profile to the manager today for {roleline}.\n{signature}",
 'missed.txt': "Hi {full}, I tried reaching you just now about your application for {roleline} - whenever you are free, please call me back or tell me a good time to connect.\n{signature}",
}
for fn in OLD:
    lp = os.path.join(DD, fn)
    try: cur = open(lp).read().strip()
    except Exception: continue
    if cur == OLD[fn].strip():
        open(lp, 'w').write(NEW[fn] + '\n'); done.append('reseed:' + fn)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S271 the draft's role comes from the position, never from a list or stage folder", "'S270 every name the skip branch speaks is defined in the same book", "ck('S271 the draft'+chr(39)+'s role comes from the position, never from a list or stage folder', (chr(35)+' POS-OF v84.18') in _src and ('def _pos_of(' in _src))"),
      ("'S272 the roleline omits what was never taught", "'S271 the draft's role comes from the position, never from a list or stage folder", "ck('S272 the roleline omits what was never taught', (chr(35)+' ROLELINE v84.18') in _src)")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
