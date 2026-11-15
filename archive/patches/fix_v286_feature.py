import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def calls_cmd(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def tags_tidy('))
    i1 = next(k for k in range(i + 1, len(B)) if B[k].startswith('def ') and not B[k].startswith('def tags_tidy'))
    B[i1:i1] = ["SHEET_PATH = os.path.join(BASE_DIR, 'sheet.json')  # CHAIR v84.10b: today's call queue lives here",
                "def sheet_load():",
                "    try: return json.load(open(SHEET_PATH))",
                "    except Exception: return {'date': '', 'items': [], 'current': None}",
                "def sheet_save(s):",
                "    try: json.dump(s, open(SHEET_PATH, 'w'), indent=1)",
                "    except Exception: pass",
                "def sheet_current(): return sheet_load().get('current')",
                "CHAIR_WORDS = {'missed': '4', 'no answer': '4', 'jd': '1', 'jd mailed': '1', 'cv': '3', 'update cv': '3', 'not interested': '2', 'ready': '5', 'manager': '5'}  # CHAIR v84.10b: the words you would say anyway",
                "def chair_word(q): return CHAIR_WORDS.get((q or '').strip().lower())",
                "OUTCOMES = {'1': ('Awaiting JD Confirmation', 'interested · JD mailed', False), '2': ('Closed \\u2013 Not Proceeding', 'not interested', False), '3': ('Awaiting CV Update', 'will update CV', False), '4': ('Call Scheduled', 'missed / no answer', True), '5': ('Ready for Manager Review', 'ready for manager', False)}",
                "def calls_cmd(arg, root, say=print):  # CHAIR v84.10b: seed today's sheet with every uncovered paper on the desk",
                "    scopes = [desk_resolve(arg, root)] if arg else (desk_paths() or [root])",
                "    items = []; seen = set()",
                "    for sc in scopes:",
                "        if not sc or not os.path.isdir(sc): continue",
                "        for dp, dn, fn in os.walk(sc):",
                "            for x in fn:",
                "                if not x.lower().endswith(('.pdf', '.docx')): continue",
                "                p = os.path.join(dp, x); rp = os.path.realpath(p)",
                "                if rp in seen: continue",
                "                seen.add(rp)",
                "                if [t for t in _tags_of(p) if _tag_stage(t)]: continue",
                "                items.append({'p': p, 'name': os.path.splitext(x)[0], 'status': 'waiting'})",
                "    sheet_save({'date': time.strftime('%Y-%m-%d'), 'items': items, 'current': None})",
                "    say(f'📞 call sheet seeded: {len(items)} uncovered candidate(s) on the desk')",
                "    if items: say('   type: up')",
                "def sheet_cmd(arg, root, say=print):",
                "    s = sheet_load()",
                "    dn = [i for i in s.get('items', []) if i['status'] != 'waiting']; wt = [i for i in s.get('items', []) if i['status'] == 'waiting']",
                "    cur = s.get('current')",
                "    say(f\"📞 sheet {s.get('date') or '-'}: covered {len(dn)} · waiting {len(wt)}\" + (f\" · NOW: {cur['name']}\" if cur else ''))",
                "    for i in dn[-8:]: say(f\"   ✅ {i['name']} · {i.get('outcome', '')}\")",
                "    for i in wt[:8]: say(f\"   ⏳ {i['name']}\")",
                "def up_cmd(arg, root, say=print):  # CHAIR v84.10b: the next waiting candidate takes the chair, dossier and all",
                "    s = sheet_load()",
                "    w = [i for i in s.get('items', []) if i['status'] == 'waiting']",
                "    if not w: say('📭 sheet empty - type: calls'); return",
                "    i = w[0]; s['current'] = i; sheet_save(s)",
                "    p = i['p']; ph = taught_digits(i['name']) or phones_of(p)",
                "    say(f\"📞 UP: {i['name']} · in {os.path.basename(os.path.dirname(p))}\")",
                "    if isinstance(ph, list): say('   phones: ' + ' · '.join(f'{n}) {d}' for n, d in enumerate(ph, 1)))",
                "    elif ph: say(f'   phone: {ph}')",
                "    else: say('   phone: none taught - teach me: python3 butler.py teach <name> <digits>')",
                "    tgs = _tags_of(p)",
                "    if tgs: say('   tags: ' + ', '.join(tgs))",
                "    say('   after the call, one digit or one word closes his row:')",
                "    say('   1 interested · JD mailed   → [Awaiting JD Confirmation]')",
                "    say('   2 not interested           → [Closed \\u2013 Not Proceeding]')",
                "    say('   3 will update CV           → [Awaiting CV Update]')",
                "    say('   4 missed / no answer       → [Call Scheduled] + WhatsApp draft')",
                "    say('   5 ready for manager review → [Ready for Manager Review]')",
                "def outcome_cmd(key, root, say=print):  # CHAIR v84.10b: the chair remembers the name; you only say what happened",
                "    s = sheet_load(); cur = s.get('current')",
                "    if not cur: say('🤷 nobody is in the chair - type: up'); return",
                "    o = OUTCOMES.get(key)",
                "    if not o: say('🤷 unknown outcome - digits 1 to 5, or missed / jd / cv / not interested / ready'); return",
                "    tag, outcome, wa_draft = o; p = cur['p']",
                "    say(f\"🤖 Proposal: {cur['name']} → [{tag}] ({outcome})\" + (' · WhatsApp missed-call draft will open, unsent' if wa_draft else '') + ' · y / n')",
                "    k = confirm_wait(say)",
                "    if k != 'y':",
                "        say('· row left open - he stays in the chair' if k == 'n' else '· row left open')",
                "        return",
                "    cur_tags = _tags_of(p)",
                "    drops = [t for t in cur_tags if _tag_stage(t) and t != tag]",
                "    newtags = [t for t in cur_tags if t not in drops] + ([tag] if tag not in cur_tags else [])",
                "    try:",
                "        _tag_write(p, newtags)",
                "        say(f\"🏷️ {cur['name']}: {tag}\" + (f' (dropped {\", \".join(drops)})' if drops else ''))",
                "        _stage_note(cur['name'], cur_tags, newtags, os.path.basename(os.path.dirname(p)), tag, 'chair')",
                "        _stage_move(p, tag, say)",
                "    except Exception as _te:",
                "        say(f'⚠️ tag write failed: {_te}'); return",
                "    for it in s.get('items', []):",
                "        if it.get('p') == p: it['status'] = 'done'; it['outcome'] = outcome; it['ts'] = int(time.time())",
                "    s['current'] = None; sheet_save(s)",
                "    if wa_draft:  # MISSED v84.10b: the missed call speaks for itself, through the number he already knows",
                "        ph = taught_digits(cur['name']) or phones_of(p)",
                "        if isinstance(ph, list): ph = ph[0]",
                "        if ph:",
                "            import wa",
                "            first = cur['name'].split()[0].title()",
                "            wa.send_review(ph, f'Hi {first}, I tried reaching you just now about your application - whenever you are free, please call me back or tell me a good time to connect.', say)",
                "        else: say(f'⚠️ no phone taught for {cur[\"name\"]} - draft skipped; teach me and retry')",
                "    w = [x for x in s.get('items', []) if x['status'] == 'waiting']  # ADVANCE v84.10b: the queue walks without being pushed",
                "    if w: say(f'⏭️ next up: {w[0][\"name\"]} - type: up')",
                "    else: say('🏁 sheet covered - every candidate has an outcome')",
                ""]
    done.append('call-chair')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if "'chase', 'tag', 'dash', 'audit', 'tidy')" in l:
        B[k] = l.replace("'chase', 'tag', 'dash', 'audit', 'tidy')", "'chase', 'tag', 'dash', 'audit', 'tidy', 'calls', 'sheet', 'up')")
        if 'cli-chair' not in done: done.append('cli-chair')
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("if len(sys.argv) > 1 and sys.argv[1].isdigit() and tag_pick_pending():"):
        d = ind(l)
        B[k:k] = [d*' ' + "if len(sys.argv) > 1 and sys.argv[1] in ('1', '2', '3', '4', '5') and sheet_current():  # CHAIR v84.10b",
                  (d+4)*' ' + "outcome_cmd(sys.argv[1], _pl_root(), print); sys.exit(0)",
                  d*' ' + "if len(sys.argv) > 1 and sheet_current() and chair_word(sys.argv[1]):",
                  (d+4)*' ' + "outcome_cmd(chair_word(sys.argv[1]), _pl_root(), print); sys.exit(0)"]
        done.append('cli-chair-route'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("elif _v == 'tidy':"):
        d = ind(l)
        B.insert(k+1, d*' ' + "elif _v == 'calls': calls_cmd(' '.join(_a), _pl_root(), print)")
        B.insert(k+2, d*' ' + "elif _v == 'sheet': sheet_cmd(' '.join(_a), _pl_root(), print)")
        B.insert(k+3, d*' ' + "elif _v == 'up': up_cmd(' '.join(_a), _pl_root(), print)")
        done.append('cli-chair-verbs'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
srcg = '\n'.join(g)
if 'def do_up(' not in srcg:
    i = next(k for k, l in enumerate(g) if l.startswith('def do_tidy('))
    g[i:i] = ["def do_calls(arg, root, say=print):  # CHAIR v84.10b",
              "    butler.calls_cmd(arg, root, say)",
              "def do_sheet(arg, root, say=print):  # CHAIR v84.10b",
              "    butler.sheet_cmd(arg, root, say)",
              "def do_up(arg, root, say=print):  # CHAIR v84.10b",
              "    butler.up_cmd(arg, root, say)",
              "def do_outcome(arg, root, say=print):  # CHAIR v84.10b",
              "    butler.outcome_cmd(arg, root, say)",
              ""]
    done.append('chat-chair-fns')
    srcg = '\n'.join(g)
if 'CHAIR v84.10b' not in srcg or 'do_outcome(q.strip()' not in srcg:
    for k, l in enumerate(g):
        if l.strip().startswith("if q.startswith('pending'): do_pending("):
            d = ind(l)
            g[k:k] = [d*' ' + "if butler.sheet_current() and q.strip() in ('1', '2', '3', '4', '5'): do_outcome(q.strip(), root); continue  # CHAIR v84.10b",
                      d*' ' + "if butler.sheet_current() and butler.chair_word(q): do_outcome(butler.chair_word(q), root); continue",
                      d*' ' + "if q == 'up' or q.startswith('up '): do_up(q[2:].strip(), root); continue",
                      d*' ' + "if q.startswith('calls'): do_calls(q[5:].strip(), root); continue",
                      d*' ' + "if q.startswith('sheet'): do_sheet(q[5:].strip(), root); continue"]
            done.append('chat-chair-dispatch'); break
    srcg = '\n'.join(g)
if srcg != open(G).read():
    ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S251 the chair remembers the name - outcomes answer without it", "'S250 the clerk offers his menu when the master forgets", "ck('S251 the chair remembers the name - outcomes answer without it', (chr(35)+' CHAIR v84.10b') in _src and ('def outcome_cmd(' in _src) and ('def sheet_current(' in _src))"),
      ("'S252 a missed call tags Call Scheduled and opens the draft, unsent", "'S251 the chair remembers the name - outcomes answer without it", "ck('S252 a missed call tags Call Scheduled and opens the draft, unsent', (chr(35)+' MISSED v84.10b') in _src)"),
      ("'S253 the sheet advances only after a confirmed outcome", "'S252 a missed call tags Call Scheduled and opens the draft, unsent", "ck('S253 the sheet advances only after a confirmed outcome', (chr(35)+' ADVANCE v84.10b') in _src)")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
