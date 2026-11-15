import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
u0 = next(k for k, l in enumerate(B) if l.startswith('def up_cmd('))
u1 = next(k for k in range(u0 + 1, len(B)) if B[k].startswith('def '))
if 'SHEET-LIVE' not in '\n'.join(B[u0:u1]):
    B[u0:u1] = ["def up_cmd(arg, root, say=print):  # CHAIR v84.10b (v84.12): the sheet breathes - covered rows leave, gone rows resolve, new papers join",
                "    s = sheet_load()",
                "    sk = skips_load()",
                "    known = set()",
                "    for it in s.get('items', []):",
                "        try: known.add(os.path.realpath(it['p']))",
                "        except Exception: pass",
                "    for it in s.get('items', []):  # SHEET-LIVE v84.12: reconcile against the living desk before seating anyone",
                "        if it.get('status') != 'waiting': continue",
                "        p = it['p']",
                "        if not os.path.exists(p):",
                "            q = _find_by_fp(it.get('fp'), root)",
                "            if q: p = it['p'] = q",
                "            else: it['status'] = 'done'; it['outcome'] = 'gone'; continue",
                "        if _tags_of(p): it['status'] = 'done'; it['outcome'] = 'covered elsewhere'; continue",
                "    for sc in desk_paths():",
                "        for dp, dn, fn in os.walk(sc):",
                "            for x in fn:",
                "                if not _is_desk_candidate(x): continue",
                "                q = os.path.join(dp, x); rq = os.path.realpath(q)",
                "                if rq in known or rq in sk or _tags_of(q): continue",
                "                s.setdefault('items', []).append({'p': q, 'name': os.path.splitext(x)[0], 'status': 'waiting', 'fp': _fp(q)})",
                "                known.add(rq)",
                "                say(f'➕ new paper joined the sheet: {x}')",
                "    sheet_save(s)",
                "    w = [i for i in s.get('items', []) if i['status'] == 'waiting']",
                "    if not w: say('📭 sheet empty - type: calls'); return",
                "    i = w[0]; s['current'] = i; sheet_save(s)",
                "    p = i['p']; ph = taught_digits(i['name']) or phones_of(p) or None",
                "    if isinstance(ph, list): ph = ph[0] if ph else None",
                "    say(f\"📞 UP: {i['name']} · in {os.path.basename(os.path.dirname(p))}\")",
                "    if isinstance(ph, list): say('   phones: ' + ' · '.join(f'{n}) {d}' for n, d in enumerate(ph, 1)))",
                "    elif ph: say(f'   phone: {ph}')",
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
    done.append('sheet-live')
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("w = [x for x in s.get('items', []) if x['status'] == 'waiting']  # ADVANCE") and 'CENSUS-AFTER' not in '\n'.join(B[max(0,k-3):k]):
        d = ind(l)
        B.insert(k, d*' ' + "desk_dashboard(say)  # CENSUS-AFTER v84.12: every closed row ends with the living scoreboard")
        done.append('census-after'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S261 the sheet breathes - covered rows leave, new papers join", "'S260 covered means any tag - the sheet seats only the silent", "ck('S261 the sheet breathes - covered rows leave, new papers join', (chr(35)+' SHEET-LIVE v84.12') in _src)"),
      ("'S262 every closed row ends with the living scoreboard", "'S261 the sheet breathes - covered rows leave, new papers join", "ck('S262 every closed row ends with the living scoreboard', (chr(35)+' CENSUS-AFTER v84.12') in _src)")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
