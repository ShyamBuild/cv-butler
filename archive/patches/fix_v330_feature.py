import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
t = open(AR).read() if os.path.exists(AR) else ''
if '## module map' not in t:
    open(AR, 'a').write("""
## module map (butler.py, from the master's def-map paste, v84.40)
xattr kernel: _xattr_raw _xattr_set_raw _xattr_del_raw _tag_write _tags_of get_tags _tag_stage _tag_vocab - what we write is what the next read sees
identity clerk: phones_in_text emails_in_text phones_of emails_of teach_phone listen_teach _full_text provenance_of polish_name standard_name get_visual_name heuristic_name - a human is confirmed by his own paper, his taught word last
conversion bench: _sniff_ext detect_engines convert_doc convert_pages convert_eml convert_msg - the reason Converted Files exists and never queues
desk and chairs: desk_load desk_resolve desk_paths desk_cmd desk_release _is_desk_candidate calls_cmd sheet_cmd options_cmd up_cmd outcome_cmd chair_word taught_digits sheet_current - folders are the truth
coverage memory: covered_load covered_add _name_key _covered_names twins_cmd forget_cmd skips_load _fp _find_by_fp - spoken-to never re-offered; a renamed paper is the same paper
registry: pos_identity say_identity_for clients_cmd client_cmd posmeta_cmd meta_cmd _pos_of _draft_fields _draft_text _sig _chair_wa_text _chair_draft _chase_draft - one truth per position, taught once, every composer drinks from it
proposal gate: confirm_wait action_pending action_cancel action_execute _stage_move _stage_note _repath_ledgers - nothing happens without the keystroke; everything is written down
errands clock: _pl_root _pl_load _pl_due _pl_age _pl_clientpos pipeline_pending pipeline_status pipeline_note chase_cmd _next_11 _clamp_window - timers arm from tags and sleep at night
census and reports: desk_dashboard tags_audit tags_tidy daily_briefing followup_cmd weekly_cmd - the desk speaks its census in one breath
rename gate: _jd_like_name _portal_name _is_candidate_paper _canonical_person_name _rename_ledger + Butler._rename/observe/latest/position_folder_for - the visual name carries the human; your word can undo it
doors: wa.send_review/_ctx/_click_send/_place_text/_arm (persistent window, thumb sends) · ad_wait.build_text/slide/pop_job (queued chases) · briefing.answer/_ear_intent/_ear_json (the ear)
""")
    done.append('module-map')
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def weekly_cmd(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def daily_briefing('))
    B[i:i] = ["def weekly_cmd(arg, root, say=print):  # WEEKLY v84.40: the manager's page - seven days of decisions, read from the stage log and the sheet",
              "    cut = time.time() - 7 * 86400",
              "    try: lg = json.load(open(os.path.join(BASE_DIR, 'stage_log.json')))",
              "    except Exception: lg = []",
              "    rows = [e for e in lg if isinstance(e, dict) and (e.get('ts') or 0) >= cut]",
              "    by = {}",
              "    for e in rows:",
              "        by.setdefault(e.get('to') or e.get('tag') or '?', []).append(os.path.basename(e.get('file') or '?'))",
              "    say(f'📅 last seven days: {len(rows)} stage decision(s)')",
              "    for k in sorted(by):",
              "        ns = by[k]",
              "        say(f'   → {k}: {len(ns)} · ' + ', '.join(ns[:6]) + (' …' if len(ns) > 6 else ''))",
              "    s = sheet_load()",
              "    done_rows = [i for i in s.get('items', []) if i.get('status') != 'waiting']",
              "    outs = {}",
              "    for i in done_rows: outs[i.get('outcome') or '?'] = outs.get(i.get('outcome') or '?', 0) + 1",
              "    if outs: say('📞 this sheet: ' + ' · '.join(f'{k}:{v}' for k, v in sorted(outs.items())))",
              "    say(f'⏭️ skipped this season: {len(skips_load())} · covered memory: {len(covered_load())}')",
              "    desk_dashboard(say)",
              ""]
    done.append('weekly')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if "'twins', 'skipfolder')" in l and 'weekly' not in l:
        B[k] = l.replace("'skipfolder')", "'skipfolder', 'weekly')")
        done.append('cli-weekly-tuple'); break
for k, l in enumerate(B):
    if l.strip().startswith("elif _v == 'skipfolder':") and 'weekly' not in '\n'.join(B[k:k+3]):
        d = ind(l)
        B.insert(k+1, d*' ' + "elif _v == 'weekly': weekly_cmd(' '.join(_a), _pl_root(), print)")
        done.append('cli-weekly-branch'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
if 'weekly_cmd' not in '\n'.join(g):
    for k, l in enumerate(g):
        if l.strip().startswith("if q.startswith('skipfolder '):"):
            d = ind(l)
            g.insert(k+1, d*' ' + "if q.strip() == 'weekly': butler.weekly_cmd('', root, say); continue  # WEEKLY v84.40")
            done.append('chat-weekly'); break
    srcg = '\n'.join(g)
    if srcg != open(G).read():
        ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S306 the weekly page reads only what the house already keeps", "'S305 every contact truth is spoken once, at the seat and at the proposal", "ck('S306 the weekly page reads only what the house already keeps', (chr(35)+' WEEKLY v84.40') in _src and ('def weekly_cmd(' in _src) and ('stage_log.json' in _src))"),
      ("'S307 the module map lives in the index, versioned with the code", "'S306 the weekly page reads only what the house already keeps", "ck('S307 the module map lives in the index, versioned with the code', os.path.exists(os.path.join(BASE_DIR, 'ARCHITECTURE.md')) and ('module map' in open(os.path.join(BASE_DIR, 'ARCHITECTURE.md')).read()))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
