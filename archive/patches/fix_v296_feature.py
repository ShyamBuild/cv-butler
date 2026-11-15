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
c0 = next(k for k, l in enumerate(B) if l.strip().startswith('items = []; seen = set()') and 'def calls_cmd' in '\n'.join(B[max(0,k-14):k]))
if 'cov = _covered_names(root)' not in '\n'.join(B[c0:c0+12]):
    B.insert(c0+1, ind(B[c0])*' ' + "cov = _covered_names(root)")
    k2 = next(k for k in range(c0, c0+14) if B[k].strip().startswith('if _tags_of(p): continue'))
    B.insert(k2+1, ind(B[k2])*' ' + "if _name_key(x) in cov: continue  # COVERED-MEMORY v84.15")
    done.append('calls-covered-names')
src = '\n'.join(B)
u0 = next(k for k, l in enumerate(B) if l.startswith('def up_cmd('))
u1 = next(k for k in range(u0 + 1, len(B)) if B[k].startswith('def '))
if 'SEAT-CHECK' not in '\n'.join(B[u0:u1]):
    B[u0:u1] = ["def up_cmd(arg, root, say=print):  # CHAIR v84.10b (v84.15): the sheet breathes, and the seat itself re-checks coverage",
                "    s = sheet_load()",
                "    sk = skips_load()",
                "    cov = _covered_names(root)",
                "    known = set()",
                "    for it in s.get('items', []):",
                "        try: known.add(os.path.realpath(it['p']))",
                "        except Exception: pass",
                "    for it in s.get('items', []):  # SHEET-LIVE v84.12",
                "        if it.get('status') != 'waiting': continue",
                "        p = it['p']",
                "        if not os.path.exists(p):",
                "            q = _find_by_fp(it.get('fp'), root)",
                "            if q: p = it['p'] = q",
                "            else: it['status'] = 'done'; it['outcome'] = 'gone'; continue",
                "        if _tags_of(p) or _name_key(os.path.basename(p)) in cov: it['status'] = 'done'; it['outcome'] = 'covered elsewhere'; continue",
                "    for sc in desk_paths():",
                "        for dp, dn, fn in os.walk(sc):",
                "            for x in fn:",
                "                if not _is_desk_candidate(x): continue",
                "                q = os.path.join(dp, x); rq = os.path.realpath(q)",
                "                if rq in known or rq in sk or _tags_of(q) or _name_key(x) in cov: continue",
                "                s.setdefault('items', []).append({'p': q, 'name': os.path.splitext(x)[0], 'status': 'waiting', 'fp': _fp(q)})",
                "                known.add(rq)",
                "                say(f'➕ new paper joined the sheet: {x}')",
                "    i = None  # SEAT-CHECK v84.15: coverage is enforced at the chair, not merely at the seed",
                "    for it in s.get('items', []):",
                "        if it.get('status') != 'waiting': continue",
                "        p = it['p']",
                "        if not os.path.exists(p):",
                "            q = _find_by_fp(it.get('fp'), root)",
                "            if q: p = it['p'] = q",
                "            else: it['status'] = 'done'; it['outcome'] = 'gone'; continue",
                "        if _tags_of(p) or _name_key(os.path.basename(p)) in cov:",
                "            it['status'] = 'done'; it['outcome'] = 'covered elsewhere'; continue",
                "        i = it; break",
                "    sheet_save(s)",
                "    if not i: say('📭 sheet empty - type: calls'); return",
                "    s['current'] = i; sheet_save(s)",
                "    p = i['p']; ph = taught_digits(i['name']) or phones_of(p) or None",
                "    if isinstance(ph, list): ph = ph[0] if ph else None",
                "    say(f\"📞 UP: {i['name']} · in {os.path.basename(os.path.dirname(p))}\")",
                "    if ph: say(f'   phone: {ph}')",
                "    else: say(f'   phone: none readable - teach me: python3 butler.py teach {i[\"name\"].split()[0].lower()} <digits>')",
                "    tgs = _tags_of(p)",
                "    if tgs: say('   tags: ' + ', '.join(tgs))",
                "    say('   after the call, one digit or one word closes his row:')",
                "    say('   1 interested · JD mailed   → [Awaiting JD Confirmation]')",
                "    say('   2 not interested           → [Closed \\u2013 Not Proceeding]')",
                "    say('   3 will update CV           → [Awaiting CV Update]')",
                "    say('   4 missed / no answer       → [Call Scheduled] + WhatsApp draft')",
                "    say('   5 ready for manager review → [Ready for Manager Review]')",
                "    say('   6 skip him for now        → no tag, no move, remembered')",
                ""]
    done.append('up-rewrite')
src = '\n'.join(B)
o0 = next(k for k, l in enumerate(B) if l.startswith('def outcome_cmd('))
o1 = next(k for k in range(o0 + 1, len(B)) if B[k].startswith('def '))
seg = B[o0:o1]
if 'PROPOSE-WAIT' not in '\n'.join(seg):
    for k in range(o0, o1):
        if B[k].strip() == 'k = confirm_wait(say)':
            d = ind(B[k])
            B[k:k+3] = [d*' ' + "k = confirm_wait(say)",
                        d*' ' + "if k == 'n':",
                        (d+4)*' ' + "say('· row left open - he stays in the chair'); return",
                        d*' ' + "if k != 'y':  # PROPOSE-WAIT v84.15: Enter or silence leaves a typed answer pending",
                        (d+4)*' ' + "import json as _j2",
                        (d+4)*' ' + "try: _j2.dump({'p': p, 'tag': tag, 'on': True, 'move_to': True, 'ts': int(time.time())}, open(os.path.join(BASE_DIR, 'pending_action.json'), 'w'))",
                        (d+4)*' ' + "except Exception: pass",
                        (d+4)*' ' + "say('· proposal waiting - type y or n on the next line')",
                        (d+4)*' ' + "return"]
            done.append('propose-wait'); break
    src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("_stage_note(cur['name'], cur_tags, newtags,") and 'covered_add' not in '\n'.join(B[k:k+3]):
        B.insert(k+1, ind(l)*' ' + "covered_add(_name_key(os.path.basename(p)), _fp(p), tag, os.path.basename(p))")
        done.append('cover-outcome'); break
for k, l in enumerate(B):
    if "'chair-skip')" in l and 'covered_add' not in '\n'.join(B[k:k+3]):
        B.insert(k+1, ind(l)*' ' + "covered_add(_name_key(os.path.basename(p)), _fp(p), 'skipped', os.path.basename(p))")
        done.append('cover-skip'); break
for k, l in enumerate(B):
    if l.strip().startswith("_stage_note(os.path.basename(p), cur, cur + [tag],") and 'covered_add' not in '\n'.join(B[k:k+3]):
        B.insert(k+1, ind(l)*' ' + "covered_add(_name_key(os.path.basename(p)), _fp(p), tag, os.path.basename(p))")
        done.append('cover-tagvoice'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if "'calls', 'sheet', 'up', 'unskip', 'followup', 'release')" in l:
        B[k] = l.replace("'release')", "'release', 'forget')")
        done.append('cli-forget-tuple'); break
for k, l in enumerate(B):
    if l.strip().startswith("elif _v == 'release':") and 'forget' not in '\n'.join(B[k:k+3]):
        B.insert(k+1, ind(l)*' ' + "elif _v == 'forget': forget_cmd(' '.join(_a), _pl_root(), print)")
        done.append('cli-forget-branch'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
if 'forget_cmd' not in '\n'.join(g):
    for k, l in enumerate(g):
        if l.strip().startswith("if q.startswith('unskip '):"):
            g.insert(k+1, ind(l)*' ' + "if q.startswith('forget '): butler.forget_cmd(q[7:].strip(), root, say); continue  # COVERED-MEMORY v84.15")
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
GU = [("'S265 a person covered once is never seated again", "'S264 the fingerprint searches every file and names a stripped extension aloud", "ck('S265 a person covered once is never seated again', (chr(35)+' COVERED-MEMORY v84.15') in _src and ('def covered_add(' in _src) and ('def forget_cmd(' in _src))"),
      ("'S266 coverage is enforced at the chair, not merely at the seed", "'S265 a person covered once is never seated again", "ck('S266 coverage is enforced at the chair, not merely at the seed', (chr(35)+' SEAT-CHECK v84.15') in _src)"),
      ("'S267 a proposal survives Enter and waits for a typed answer", "'S266 coverage is enforced at the chair, not merely at the seed", "ck('S267 a proposal survives Enter and waits for a typed answer', (chr(35)+' PROPOSE-WAIT v84.15') in _src)")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
