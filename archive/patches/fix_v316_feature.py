import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'PHONE-FIRST' not in src:
    for k, l in enumerate(B):
        if l.strip().startswith('cur_tags = _tags_of(p)') and 'def outcome_cmd' in '\n'.join(B[max(0,k-40):k]):
            B.insert(k, ind(l)*' ' + "ph0 = taught_digits(cur['name']) or phones_of(p) or None  # PHONE-FIRST v84.31: read the number before the paper moves, never from a ghost path")
            done.append('phone-first'); break
    src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("ph = taught_digits(cur['name']) or phones_of(p) or None"):
        B[k] = ind(l)*' ' + "ph = ph0"
        done.append('phone-use'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
DD = os.path.expanduser('~/CV_Tool/drafts')
OLD = {
 'cv.txt': "Hi {full}, as discussed on call, please share your updated CV at the earliest so I can push your profile to the manager today for {roleline}.\n{signature}",
 'missed.txt': "Hi {full}, I tried reaching you just now about your application for {roleline} - whenever you are free, please call me back or tell me a good time to connect.\n{signature}",
}
NEW = {
 'cv.txt': "Hi {full}, as discussed on call, I have shared the JD for {roleline} on your email - kindly acknowledge receipt, and whenever your updated CV is ready please share it here in PDF or on the email chain, so I can move your profile to the manager today.\n{signature}",
 'missed.txt': "Hi {full}, I tried calling you today regarding {roleline} but couldn't reach you. I have shared the JD on your email - kindly check it and let me know a good time to reconnect, or share your updated CV in PDF here if ready.\n{signature}",
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
GU = [("'S290 the draft's phone is read before the paper moves", "'S289 a bare keyword during a call speaks to the seated candidate", "ck('S290 the draft'+chr(39)+'s phone is read before the paper moves', (chr(35)+' PHONE-FIRST v84.31') in _src and ('ph = ph0' in _src))"),
      ("'S291 the cv and missed drafts carry the JD-acknowledgement touchpoint", "'S290 the draft's phone is read before the paper moves", "ck('S291 the cv and missed drafts carry the JD-acknowledgement touchpoint', 'acknowledge receipt' in open(os.path.join(BASE_DIR, 'drafts', 'cv.txt')).read() and 'JD on your email' in open(os.path.join(BASE_DIR, 'drafts', 'missed.txt')).read())")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
