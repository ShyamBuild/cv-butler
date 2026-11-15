import ast, os, json
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def covered_add(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def skips_load('))
    B[i:i] = ["COVERED_PATH = os.path.join(BASE_DIR, 'covered.json')  # COVERED-MEMORY v84.15: a person covered once is not offered again",
              "def covered_load():",
              "    try: return json.load(open(COVERED_PATH))",
              "    except Exception: return {}",
              "def covered_add(nk, fp, tag, file):",
              "    d = covered_load(); d[nk] = {'ts': int(time.time()), 'fp': fp, 'tag': tag, 'file': file}",
              "    try: json.dump(d, open(COVERED_PATH, 'w'), indent=1)",
              "    except Exception: pass",
              "def _name_key(x):",
              "    import re as _re",
              "    return ' '.join(_re.sub(r'[^a-z ]', ' ', os.path.splitext(x)[0].lower()).split())",
              "def _covered_names(root):  # COVERED-MEMORY v84.15: memory plus the living desk, by person not by file",
              "    keys = set(covered_load())",
              "    seen = set()",
              "    for sc in desk_paths() or [root]:",
              "        for dp, dn, fn in os.walk(sc):",
              "            for x in fn:",
              "                if not _is_desk_candidate(x): continue",
              "                q = os.path.join(dp, x); rq = os.path.realpath(q)",
              "                if rq in seen: continue",
              "                seen.add(rq)",
              "                if [t for t in _tags_of(q) if _tag_stage(t)]: keys.add(_name_key(x))",
              "    return keys",
              "def forget_cmd(arg, root, say=print):  # COVERED-MEMORY v84.15: the door that re-opens a person for a new season",
              "    d = covered_load(); nk = _name_key(arg + '.pdf')",
              "    hit = [k for k in d if k == nk or (arg and arg.lower() in k)]",
              "    if not hit: say(f'🤷 no covered memory matches {arg!r}'); return",
              "    for k in hit: d.pop(k, None)",
              "    json.dump(d, open(COVERED_PATH, 'w'), indent=1)",
              "    say('↩️ forgotten: ' + ', '.join(hit) + ' - the next calls may seat them again')",
              ""]
    done.append('covered-memory')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("if _tags_of(p): continue  # COVERED v84.11") and 'cov' not in '\n'.join(B[max(0,k-8):k]):
        d = ind(l)
        c0 = next(m for m in range(k, -1, -1) if B[m].strip().startswith('items = []; seen = set()'))
        B.insert(c0+1, d*' ' + "cov = _covered_names(root)")
        B.insert(k+2, d*' ' + "if _name_key(x) in cov: continue  # COVERED-MEMORY v84.15")
        done.append('calls-covered-names'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("if rq in known or rq in sk or _tags_of(q): continue") and 'cov' not in l:
        d = ind(l)
        B.insert(k+1, d*' ' + "if _name_key(x) in cov: continue  # COVERED-MEMORY v84.15")
        done.append('up-covered-names'); break
    if l.strip().startswith('sk = skips_load()') and 'def up_cmd' in '\n'.join(B[max(0,k-6):k]):
        B.insert(k+1, ind(l)*' ' + "cov = _covered_names(root)")
        done.append('up-cov-init')
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("_stage_note(cur['name'], cur_tags, newtags,") and 'covered_add' not in '\n'.join(B[k:k+3]):
        d = ind(l)
        B.insert(k+1, d*' ' + "covered_add(_name_key(os.path.basename(p)), _fp(p), tag, os.path.basename(p))")
        done.append('cover-outcome'); break
for k, l in enumerate(B):
    if "'chair-skip')" in l and 'covered_add' not in '\n'.join(B[k:k+3]):
        d = ind(l)
        B.insert(k+1, d*' ' + "covered_add(_name_key(os.path.basename(p)), _fp(p), 'skipped', os.path.basename(p))")
        done.append('cover-skip'); break
for k, l in enumerate(B):
    if l.strip().startswith("_stage_note(os.path.basename(p), cur, cur + [tag],") and 'covered_add' not in '\n'.join(B[k:k+3]):
        d = ind(l)
        B.insert(k+1, d*' ' + "covered_add(_name_key(os.path.basename(p)), _fp(p), tag, os.path.basename(p))")
        done.append('cover-tagvoice'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if "'calls', 'sheet', 'up', 'unskip', 'followup', 'release')" in l:
        B[k] = l.replace("'release')", "'release', 'forget')")
        done.append('cli-forget-tuple'); break
for k, l in enumerate(B):
    if l.strip().startswith("elif _v == 'release':") and 'forget' not in '\n'.join(B[k:k+3]):
        d = ind(l)
        B.insert(k+1, d*' ' + "elif _v == 'forget': forget_cmd(' '.join(_a), _pl_root(), print)")
        done.append('cli-forget-branch'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
if 'forget' not in '\n'.join(g):
    for k, l in enumerate(g):
        if l.strip().startswith("if q.startswith('unskip '):"):
            d = ind(l)
            g.insert(k+1, d*' ' + "if q.startswith('forget '): butler.forget_cmd(q[7:].strip(), root, say); continue  # COVERED-MEMORY v84.15")
            done.append('chat-forget'); break
    srcg = '\n'.join(g)
    if srcg != open(G).read():
        ast.parse(srcg); open(G, 'w').write(srcg)
DD = os.path.expanduser('~/CV_Tool/drafts')
os.makedirs(DD, exist_ok=True)
TPL = {
 'refer.txt': "Hi {full}, thank you for your time today. I have noted you are not keen on the role of {role} in {company} for {loc} location - if any friend or colleague might fit, do refer them to me. I have shared the JD on email for your reference. Wishing you the very best.\n{signature}",
 'jd.txt': "Hi {full}, great speaking with you today. I have shared the JD for the role of {role} in {company} for {loc} location on your email - please go through it and confirm your interest so I can move your profile forward.\n{signature}",
 'cv.txt': "Hi {full}, as discussed on call, please share your updated CV at the earliest so I can push your profile to the manager today for the role of {role} in {company}.\n{signature}",
 'missed.txt': "Hi {full}, I tried reaching you just now about your application for {role} in {company} - whenever you are free, please call me back or tell me a good time to connect.\n{signature}",
}
for fn, txt in TPL.items():
    lp = os.path.join(DD, fn)
    if not os.path.exists(lp):
        open(lp, 'w').write(txt + '\n'); done.append('seed:' + fn)
sp = os.path.expanduser('~/CV_Tool/signature.txt')
if not os.path.exists(sp):
    open(sp, 'w').write('Regards,\nSundeep Rana\n'); done.append('seed:signature')
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S265 a person covered once is never seated again", "'S264 the fingerprint searches every file and names a stripped extension aloud", "ck('S265 a person covered once is never seated again', (chr(35)+' COVERED-MEMORY v84.15') in _src and ('def covered_add(' in _src) and ('def forget_cmd(' in _src))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
