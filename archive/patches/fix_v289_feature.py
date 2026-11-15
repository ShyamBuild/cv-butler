import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def _chair_draft(' not in src:
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
              ""]
    done.append('skip-drafts')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("OUTCOMES = {'1':"):
        d = ind(l)
        B[k] = d*' ' + "OUTCOMES = {'1': ('Awaiting JD Confirmation', 'interested · JD mailed', 'jd'), '2': ('Closed \\u2013 Not Proceeding', 'not interested', 'refer'), '3': ('Awaiting CV Update', 'will update CV', 'cv'), '4': ('Call Scheduled', 'missed / no answer', 'missed'), '5': ('Ready for Manager Review', 'ready for manager', None), '6': (None, 'skipped', None)}  # DRAFTS v84.11: outward outcomes speak, internal ones stay silent"
        done.append('outcomes-6'); break
src = '\n'.join(B)
o0 = next(k for k, l in enumerate(B) if l.startswith('def outcome_cmd('))
o1 = next(k for k in range(o0 + 1, len(B)) if B[k].startswith('def '))
body = '\n'.join(B[o0:o1])
if 'skips.json' not in body and 'SKIPS_PATH' not in body:
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
    src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("say('   5 ready for manager review") and '6 skip' not in '\n'.join(B[k:k+3]):
        d = ind(l)
        B.insert(k+1, d*' ' + "say('   6 skip him for now        → no tag, no move, remembered')")
        done.append('menu-6'); break
src = '\n'.join(B)
src = src.replace("CHAIR_WORDS = {'missed': '4', 'no answer': '4', 'jd': '1', 'jd mailed': '1', 'cv': '3', 'update cv': '3', 'not interested': '2', 'ready': '5', 'manager': '5'}",
                  "CHAIR_WORDS = {'missed': '4', 'no answer': '4', 'jd': '1', 'jd mailed': '1', 'cv': '3', 'update cv': '3', 'not interested': '2', 'ready': '5', 'manager': '5', 'skip': '6', 'skip him': '6'}")
if "'skip': '6'" in src and 'chair-words-6' not in done: done.append('chair-words-6')
src = src.replace("sys.argv[1] in ('1', '2', '3', '4', '5') and sheet_current()", "sys.argv[1] in ('1', '2', '3', '4', '5', '6') and sheet_current()")
src = src.replace("'chase', 'tag', 'dash', 'audit', 'tidy', 'calls', 'sheet', 'up')", "'chase', 'tag', 'dash', 'audit', 'tidy', 'calls', 'sheet', 'up', 'unskip')")
if 'def unskip_cmd(' in src and "elif _v == 'up':" in src and "elif _v == 'unskip':" not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith("elif _v == 'up':"))
    d = ind(B[i])
    B.insert(i+1, d*' ' + "elif _v == 'unskip': unskip_cmd(' '.join(_a), _pl_root(), print)")
    done.append('cli-unskip')
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if l.strip().startswith("if rp in seen: continue") and 'skips' not in '\n'.join(B[max(0,k-6):k]) and l.count('rp in seen') == 1:
        pass
src = '\n'.join(B)
if 'sk = skips_load()' not in src.split('def calls_cmd(')[1].split('def sheet_cmd(')[0]:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('if rp in seen: continue') and k > next(m for m, l2 in enumerate(B) if l2.startswith('def calls_cmd(')))
    d = ind(B[i])
    B.insert(i+1, d*' ' + "if os.path.realpath(p) in skips_load(): continue  # SKIP v84.11: the remembered stay out of tomorrow's queue")
    done.append('calls-skip-filter')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("line = ' · '.join(f'{short[t]}:{counts[t]}'"):
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
            done.append('chat-unskip'); break
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
      ("'S257 outward outcomes draft, internal outcomes stay silent", "'S256 a skip is remembered, untagged, unmoved and silent", "ck('S257 outward outcomes draft, internal outcomes stay silent', (chr(35)+' DRAFTS v84.11') in _src and ('def _chair_draft(' in _src))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
