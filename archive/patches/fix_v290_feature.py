import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
if 'def _chair_draft(' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.startswith('def outcome_cmd('))
    B[i:i] = ["SKIPS_PATH = os.path.join(BASE_DIR, 'skips.json')  # SKIP v84.11: today's list, not today's verdicts",
              "def skips_load():",
              "    try: return json.load(open(SKIPS_PATH))",
              "    except Exception: return {}",
              "def _chair_draft(kind, name, pos):  # DRAFTS v84.11: every outward outcome speaks; the internal ones stay silent",
              "    first = (name or '').split()[0].title()",
              "    if kind == 'jd': return f'Hi {first}, great speaking with you today. I have shared the JD for {pos} on your email - please go through it and confirm your interest so I can move your profile forward.'",
              "    if kind == 'cv': return f'Hi {first}, as discussed on call, please share your updated CV at the earliest so I can push your profile to the manager today.'",
              "    if kind == 'refer': return f'Hi {first}, thank you for your time today. I have noted you are not keen on this role - if any friend or colleague might fit, do refer them to me. Wishing you the very best.'",
              "    if kind == 'missed': return f'Hi {first}, I tried reaching you just now about your application - whenever you are free, please call me back or tell me a good time to connect.'",
              "    return None",
              "def unskip_cmd(arg, root, say=print):  # SKIP v84.11",
              "    sk = skips_load(); hit = [k for k in sk if arg and arg.lower() in os.path.basename(k).lower()]",
              "    if not hit: say(f'🤷 no skipped candidate matches {arg!r}'); return",
              "    for k in hit: sk.pop(k, None)",
              "    json.dump(sk, open(SKIPS_PATH, 'w'), indent=1)",
              "    say('↩️ unskipped: ' + ', '.join(os.path.basename(k) for k in hit) + ' - the next calls will seat them again')",
              "def followup_cmd(arg, root, say=print):  # FOLLOWUP v84.11: the debts, by name, not by count",
              "    seen = set(); jd = []; cv = []",
              "    for sc in desk_paths():",
              "        for dp, dn, fn in os.walk(sc):",
              "            for x in fn:",
              "                if not _is_desk_candidate(x): continue",
              "                p = os.path.join(dp, x); rp = os.path.realpath(p)",
              "                if rp in seen: continue",
              "                seen.add(rp)",
              "                tgs = _tags_of(p)",
              "                if 'Awaiting JD Confirmation' in tgs: jd.append((x, os.path.basename(dp)))",
              "                if 'Awaiting CV Update' in tgs: cv.append((x, os.path.basename(dp)))",
              "    say(f'📬 awaiting JD acknowledgement: {len(jd)}')",
              "    for x, f in jd[:10]: say(f'   · {x} · in {f}')",
              "    say(f'📬 awaiting CV update: {len(cv)}')",
              "    for x, f in cv[:10]: say(f'   · {x} · in {f}')",
              "    due = []",
              "    try:",
              "        er = json.load(open(os.path.join(BASE_DIR, 'errands.json')))",
              "        for p, e in er.items():",
              "            if isinstance(e, dict) and any(k.endswith(':chased') for k in e): due.append(os.path.basename(p))",
              "    except Exception: pass",
              "    if due: say('📨 chase due now: ' + ', '.join(due[:6]) + ' - chase send <name> opens the draft')",
              "    else: say('📨 no chase due right now')",
              ""]
    done.append('skip-drafts-followup')
for k, l in enumerate(B):
    if l.strip().startswith("OUTCOMES = {'1':") and "'6':" not in l:
        d = ind(l)
        B[k] = d*' ' + "OUTCOMES = {'1': ('Awaiting JD Confirmation', 'interested · JD mailed', 'jd'), '2': ('Closed \\u2013 Not Proceeding', 'not interested', 'refer'), '3': ('Awaiting CV Update', 'will update CV', 'cv'), '4': ('Call Scheduled', 'missed / no answer', 'missed'), '5': ('Ready for Manager Review', 'ready for manager', None), '6': (None, 'skipped', None)}  # DRAFTS v84.11: outward outcomes speak, internal ones stay silent"
        done.append('outcomes-6'); break
o0 = next(k for k, l in enumerate(B) if l.startswith('def outcome_cmd('))
o1 = next(k for k in range(o0 + 1, len(B)) if B[k].startswith('def '))
if 'SKIPPED, untagged, unmoved' not in '\n'.join(B[o0:o1]):
    B[o0:o1] = ["def outcome_cmd(key, root, say=print):  # CHAIR v84.10b (v84.11): the chair remembers the name; you only say what happened",
                "    s = sheet_load(); cur = s.get('current')",
                "    if not cur: say('🤷 nobody is in the chair - type: up'); return",
                "    o = OUTCOMES.get(key)",
                "    if not o: say('🤷 unknown outcome - digits 1 to 6, or missed / jd / cv / not interested / ready / skip'); return",
                "    tag, outcome, draft = o; p = cur['p']",
                "    say(f\"🤖 Proposal: {cur['name']} → \" + (f'[{tag}]' if tag else 'SKIPPED, untagged, unmoved') + f\" ({outcome})\" + (f' · WhatsApp {draft} draft will open, unsent' if draft else ' · no message - this one stays in the house') + ' · y / n')",
                "    k = confirm_wait(say)",
                "    if k != 'y':",
                "        say('· row left open - he stays in the chair' if k == 'n' else '· row left open')",
                "        return",
                "    if tag is None:  # SKIP v84.11: remembered, untagged, unmoved, silent",
                "        sk = skips_load(); sk[os.path.realpath(p)] = {'name': cur['name'], 'ts': int(time.time()), 'in': os.path.basename(os.path.dirname(p))}",
                "        json.dump(sk, open(SKIPS_PATH, 'w'), indent=1)",
                "        for it in s.get('items', []):",
                "            if it.get('p') == p: it['status'] = 'done'; it['outcome'] = 'skipped'; it['ts'] = int(time.time())",
                "        s['current'] = None; sheet_save(s)",
                "        _stage_note(cur['name'], _tags_of(p), _tags_of(p), os.path.basename(os.path.dirname(p)), os.path.basename(os.path.dirname(p)), 'chair-skip')",
                "        say(f\"⏭️ skipped {cur['name']} - untagged, unmoved, remembered; unskip {cur['name'].split()[0].lower()} brings him back\")",
                "    else:",
                "        cur_tags = _tags_of(p)",
                "        drops = [t for t in cur_tags if _tag_stage(t) and t != tag]",
                "        newtags = [t for t in cur_tags if t not in drops] + ([tag] if tag not in cur_tags else [])",
                "        try:",
                "            _tag_write(p, newtags)",
                "            say(f\"🏷️ {cur['name']}: {tag}\" + (f' (dropped {\", \".join(drops)})' if drops else ''))",
                "            _stage_note(cur['name'], cur_tags, newtags, os.path.basename(os.path.dirname(p)), tag, 'chair')",
                "            _stage_move(p, tag, say)",
                "        except Exception as _te:",
                "            say(f'⚠️ tag write failed: {_te}'); return",
                "        for it in s.get('items', []):",
                "            if it.get('p') == p: it['status'] = 'done'; it['outcome'] = outcome; it['ts'] = int(time.time())",
                "        s['current'] = None; sheet_save(s)",
                "        if draft:",
                "            ph = taught_digits(cur['name']) or phones_of(p)",
                "            if isinstance(ph, list): ph = ph[0]",
                "            if ph:",
                "                parts = os.path.relpath(p, root).split(os.sep)",
                "                pos = parts[-2] if len(parts) >= 3 else (desk_load().get('primary') or root).rsplit('/', 1)[-1]",
                "                import wa",
                "                wa.send_review(ph, _chair_draft(draft, cur['name'], pos), say)",
                "            else: say(f'⚠️ no phone taught for {cur[\"name\"]} - draft skipped; teach me and retry')",
                "    w = [x for x in s.get('items', []) if x['status'] == 'waiting']  # ADVANCE v84.10b: the queue walks without being pushed",
                "    if w: say(f'⏭️ next up: {w[0][\"name\"]} - type: up')",
                "    else: say('🏁 sheet covered - every candidate has an outcome')",
                ""]
    done.append('outcome-rewrite')
for k, l in enumerate(B):
    if l.strip().startswith("say('   5 ready for manager review") and '6 skip' not in '\n'.join(B[k:k+3]):
        d = ind(l)
        B.insert(k+1, d*' ' + "say('   6 skip him for now        → no tag, no move, remembered')")
        done.append('menu-6'); break
for k, l in enumerate(B):
    if l.strip().startswith('CHAIR_WORDS =') and "'skip': '6'" not in l:
        B[k] = l.rstrip()[:-0] if False else l.replace("}", ", 'skip': '6', 'skip him': '6'}") if not l.rstrip().endswith('}') else l[:l.rstrip().rfind('}')] + ", 'skip': '6', 'skip him': '6'}"
        done.append('chair-words-6'); break
for k, l in enumerate(B):
    if "sys.argv[1] in ('1', '2', '3', '4', '5') and sheet_current()" in l:
        B[k] = l.replace("('1', '2', '3', '4', '5')", "('1', '2', '3', '4', '5', '6')")
        done.append('cli-digit-6'); break
for k, l in enumerate(B):
    if "'calls', 'sheet', 'up')" in l and 'sys.argv' in l:
        B[k] = l.replace("'calls', 'sheet', 'up')", "'calls', 'sheet', 'up', 'unskip', 'followup')")
        done.append('cli-tuple'); break
for k, l in enumerate(B):
    if l.strip().startswith("elif _v == 'up':") and 'unskip' not in '\n'.join(B[k:k+4]):
        d = ind(l)
        B.insert(k+1, d*' ' + "elif _v == 'unskip': unskip_cmd(' '.join(_a), _pl_root(), print)")
        B.insert(k+2, d*' ' + "elif _v == 'followup': followup_cmd(' '.join(_a), _pl_root(), print)")
        done.append('cli-branches'); break
if 'skips_load(): continue' not in '\n'.join(B):
    c0 = next(k for k, l in enumerate(B) if l.startswith('def calls_cmd('))
    i = next(k for k in range(c0, len(B)) if B[k].strip().startswith('if rp in seen: continue'))
    d = ind(B[i])
    B.insert(i+1, d*' ' + "if os.path.realpath(p) in skips_load(): continue  # SKIP v84.11: the remembered stay out of tomorrow's queue")
    done.append('calls-skip-filter')
for k, l in enumerate(B):
    if l.strip().startswith("line = ' · '.join(f'{short[t]}:{counts[t]}'") and 'skipped:' not in l:
        d = ind(l)
        B.insert(k, d*' ' + "_sk = sum(1 for q in skips_load() if any(q.startswith(os.path.realpath(sc)) for sc in desk_paths()))")
        B[k+1] = d*' ' + "line = ' · '.join(f'{short[t]}:{counts[t]}' for t in order if counts.get(t)) + (f' · skipped:{_sk}' if _sk else '')"
        done.append('dash-skipped'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
for k, l in enumerate(g):
    if "q.strip() in ('1', '2', '3', '4', '5')" in l:
        g[k] = l.replace("('1', '2', '3', '4', '5')", "('1', '2', '3', '4', '5', '6')")
        done.append('chat-digit-6'); break
srcg = '\n'.join(g)
if 'unskip' not in srcg:
    for k, l in enumerate(g):
        if l.strip().startswith("if q.startswith('sheet'): do_sheet("):
            d = ind(l)
            g.insert(k+1, d*' ' + "if q.startswith('unskip '): butler.unskip_cmd(q[7:].strip(), root, say); continue  # SKIP v84.11")
            g.insert(k+2, d*' ' + "if q.startswith('followup'): butler.followup_cmd(q[8:].strip(), root, say); continue  # FOLLOWUP v84.11")
            done.append('chat-followup'); break
    srcg = '\n'.join(g)
if srcg != open(G).read():
    ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S256 a skip is remembered, untagged, unmoved and silent", "'S255 the sheet seats humans, not JDs or summaries", "ck('S256 a skip is remembered, untagged, unmoved and silent', (chr(35)+' SKIP v84.11') in _src and ('skips.json' in _src) and ('def unskip_cmd(' in _src))"),
      ("'S257 outward outcomes draft, internal outcomes stay silent", "'S256 a skip is remembered, untagged, unmoved and silent", "ck('S257 outward outcomes draft, internal outcomes stay silent', (chr(35)+' DRAFTS v84.11') in _src and ('def _chair_draft(' in _src))"),
      ("'S258 followup names the debtors, not merely counts them", "'S257 outward outcomes draft, internal outcomes stay silent", "ck('S258 followup names the debtors, not merely counts them', (chr(35)+' FOLLOWUP v84.11') in _src and ('def followup_cmd(' in _src))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
