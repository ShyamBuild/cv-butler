import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def _stage_note(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def _stage_move('))
    B[i:i] = ["def _stage_note(file, from_tag, to_tag, from_dir, to_dir, srcs):  # STAGE-LOG v84.4: every change is written down, with the door that made it",
              "    import json as _j",
              "    lp = os.path.join(BASE_DIR, 'stage_log.json')",
              "    try: log = _j.load(open(lp))",
              "    except Exception: log = []",
              "    log.append({'ts': int(time.time()), 'file': file, 'from_tag': from_tag, 'to_tag': to_tag, 'from_dir': from_dir, 'to_dir': to_dir, 'src': srcs})",
              "    try: _j.dump(log[-400:], open(lp, 'w'), indent=1)",
              "    except Exception: pass",
              "def action_pending():  # PROPOSE-FIRST v84.4",
              "    import json as _j",
              "    try: return _j.load(open(os.path.join(BASE_DIR, 'pending_action.json'))).get('ts', 0) > time.time() - 600",
              "    except Exception: return False",
              "def action_cancel(say=print):",
              "    try: os.remove(os.path.join(BASE_DIR, 'pending_action.json'))",
              "    except Exception: pass",
              "    say('🗑️ proposal discarded - nothing changed')",
              "def action_execute(say=print):  # PROPOSE-FIRST v84.4: the yes that makes it so",
              "    import json as _j",
              "    pp = os.path.join(BASE_DIR, 'pending_action.json')",
              "    try: pend = _j.load(open(pp))",
              "    except Exception: say('🤷 no proposal is waiting'); return",
              "    p, tag, on = pend.get('p'), pend.get('tag'), pend.get('on', True)",
              "    cur = _tags_of(p)",
              "    drops = [t for t in cur if t in _tag_vocab() and t != tag] if on else []",
              "    newtags = ([t for t in cur if t not in drops] + [tag]) if on else [t for t in cur if t != tag]",
              "    try:",
              "        _tag_write(p, newtags)",
              "        say(f\"🏷️ {os.path.basename(p)}: {tag if on else 'untagged'}\" + (f' (dropped {\", \".join(drops)})' if drops else ''))",
              "        _stage_note(os.path.basename(p), cur, newtags, os.path.basename(os.path.dirname(p)), os.path.basename(os.path.dirname(p)), 'chat/terminal')",
              "    except Exception as _te:",
              "        say(f'⚠️ tag write failed: {_te}'); return",
              "    if pend.get('move_to'):",
              "        _stage_move(p, tag, say)",
              "    try: os.remove(pp)",
              "    except Exception: pass",
              ""]
    done.append('stage-log-propose')
    src = '\n'.join(B)
i = next(k for k, l in enumerate(B) if l.startswith('def _tag_apply_one('))
i1 = next(k for k in range(i + 1, len(B)) if B[k].startswith('def '))
if 'STAGE-ONE' not in '\n'.join(B[i:i1]):
    B[i:i1] = ["def _tag_apply_one(p, tag, on, say=print):  # TAG-VOICE v84.2c (v84.4): one stage per paper, proposals before replacements",
                "    import json as _j",
                "    cur = _tags_of(p)",
                "    if not on:",
                "        if tag in cur: _tag_write(p, [t for t in cur if t != tag]); say(f'🏷️ untagged {os.path.basename(p)}: {tag}'); _stage_note(os.path.basename(p), cur, [t for t in cur if t != tag], os.path.basename(os.path.dirname(p)), os.path.basename(os.path.dirname(p)), 'chat/terminal')",
                "        else: say(f'🏷️ {os.path.basename(p)} already lacks {tag} - nothing changed')",
                "        return",
                "    drops = [t for t in cur if t in _tag_vocab() and t != tag]  # STAGE-ONE v84.4: a paper rests in one stage",
                "    move_to = None; conflict = False",
                "    root = _pl_root(); parts = os.path.relpath(p, root).split(os.sep)",
                "    if len(parts) >= 4 and parts[-2] in _tag_vocab(): pos = os.path.join(root, *parts[:-2])",
                "    elif len(parts) == 3: pos = os.path.join(root, *parts[:-1])",
                "    else: pos = None",
                "    if pos:",
                "        tgt = os.path.join(pos, tag)",
                "        if os.path.realpath(os.path.dirname(p)) != os.path.realpath(tgt):",
                "            if os.path.exists(os.path.join(tgt, os.path.basename(p))): conflict = True",
                "            else: move_to = tgt",
                "    if drops or move_to or conflict:  # PROPOSE-FIRST v84.4: real changes earn a question",
                "        txt = f\"🤖 Proposal: {os.path.basename(p)} → {tag}\"",
                "        if drops: txt += f' (drops {\", \".join(drops)})'",
                "        if move_to: txt += f' · move {os.path.basename(os.path.dirname(p))} → {tag}'",
                "        if conflict: txt += f' · a paper already rests in {tag}, so it will be tagged in place'",
                "        say(txt + ' · reply y / n')",
                "        try: _j.dump({'p': p, 'tag': tag, 'on': on, 'move_to': move_to and not conflict, 'ts': int(time.time())}, open(os.path.join(BASE_DIR, 'pending_action.json'), 'w'))",
                "        except Exception: pass",
                "        return",
                "    _tag_write(p, cur + [tag]); say(f'🏷️ tagged {os.path.basename(p)}: {tag}')",
                "    _stage_note(os.path.basename(p), cur, cur + [tag], os.path.basename(os.path.dirname(p)), os.path.basename(os.path.dirname(p)), 'chat/terminal')",
                "    _stage_move(p, tag, say)",
                ""]
    done.append('tag-apply-v844')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("if cur is None:") and 'closed' in '\n'.join(B[k:k+3]) and 'FINDER-MOVE' not in src:
        d = ind(l)
        B[k:k] = [d*' ' + "if not os.path.exists(p):  # FINDER-MOVE v84.4: a paper dragged by hand is repathed, not mourned",
                  d*' ' + "    _mv = None",
                  d*' ' + "    for _sc in (desk_paths() or [root]):",
                  d*' ' + "        for _dp, _dn, _fn in os.walk(_sc):",
                  d*' ' + "            if os.path.basename(p) in _fn:",
                  d*' ' + "                _cand = os.path.join(_dp, os.path.basename(p))",
                  d*' ' + "                if _cand != p and e.get('tag') in _tags_of(_cand): _mv = _cand; break",
                  d*' ' + "        if _mv: break",
                  d*' ' + "    if _mv:",
                  d*' ' + "        led[_mv] = led.pop(p); _repath_ledgers(p, _mv); changed = True",
                  d*' ' + "        _stage_note(os.path.basename(p), e.get('tag'), e.get('tag'), os.path.basename(os.path.dirname(p)), os.path.basename(os.path.dirname(_mv)), 'finder')",
                  d*' ' + "        say(f\"👀 noticed in Finder: {os.path.basename(p)} now rests in {os.path.basename(os.path.dirname(_mv))}\"); continue",
                  d*' ' + "    e['history'].append([e['tag'], e['since'], now]); e['closed'] = now; e['closed_tag'] = 'file gone'; changed = True",
                  d*' ' + "    say(f\"📔 {os.path.basename(p)} left the pipeline (file gone)\"); continue"]
        done.append('finder-move'); break
src = '\n'.join(B)
if 'FINDER-MOVE' in src and 'noticed in Finder: ' in src:
    for k, l in enumerate(B):
        if l.strip().startswith("if cur is None:") and 'tag removed' in '\n'.join(B[k:k+4]) and 'FINDER-TAGNOTE' not in src:
            d = ind(l)
            B.insert(k, d*' ' + "if cur != e.get('tag') and e.get('tag') in _tag_vocab() and cur in _tag_vocab():  # FINDER-TAGNOTE v84.4: a tag changed by hand is noted by the watcher")
            B.insert(k+1, (d+4)*' ' + "_stage_note(os.path.basename(p), e.get('tag'), cur, os.path.basename(os.path.dirname(p)), os.path.basename(os.path.dirname(p)), 'finder')")
            done.append('finder-tagnote'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
srcg = '\n'.join(g)
if 'def do_confirm(' not in srcg:
    i = next(k for k, l in enumerate(g) if l.startswith('def do_tagcmd('))
    g[i:i] = ["def do_confirm(arg, root, say=print):  # PROPOSE-FIRST v84.4",
              "    butler.action_execute(say)",
              "def do_cancel(arg, root, say=print):  # PROPOSE-FIRST v84.4",
              "    butler.action_cancel(say)",
              ""]
    done.append('confirm-fns')
    srcg = '\n'.join(g)
if 'TAG-PICK-ROUTE v84.3: a bare digit' in srcg and 'PROPOSE-ROUTE v84.4' not in srcg:
    for k, l in enumerate(g):
        if 'TAG-PICK-ROUTE v84.3: a bare digit' in l:
            d = ind(l)
            g[k:k] = [d*' ' + "if q.strip().lower() in ('y', 'yes', 'ok', 'confirm') and butler.action_pending(): do_confirm(q, root); continue  # PROPOSE-ROUTE v84.4",
                      d*' ' + "if q.strip().lower() in ('n', 'no', 'cancel') and butler.action_pending(): do_cancel(q, root); continue"]
            done.append('confirm-dispatch'); break
    srcg = '\n'.join(g)
if srcg != open(G).read():
    ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if l.strip().startswith("if len(sys.argv) > 1 and sys.argv[1].isdigit() and tag_pick_pending():"):
        d = ind(l)
        B[k:k] = [d*' ' + "if len(sys.argv) > 1 and sys.argv[1].lower() in ('y', 'yes', 'ok', 'confirm') and action_pending():  # PROPOSE-ROUTE v84.4",
                  (d+4)*' ' + "action_execute(print); sys.exit(0)",
                  d*' ' + "if len(sys.argv) > 1 and sys.argv[1].lower() in ('n', 'no', 'cancel') and action_pending():",
                  (d+4)*' ' + "action_cancel(print); sys.exit(0)"]
        done.append('cli-confirm'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S236 a paper rests in one stage at a time", "'S235 a tagged paper rests in its tag's folder", "ck('S236 a paper rests in one stage at a time', (chr(35)+' STAGE-ONE v84.4') in _src)"),
      ("'S237 changes that replace or move ask first", "'S236 a paper rests in one stage at a time", "ck('S237 changes that replace or move ask first', (chr(35)+' PROPOSE-FIRST v84.4') in _src and ('pending_action.json' in _src))"),
      ("'S238 every tag and move is written in the stage log", "'S237 changes that replace or move ask first", "ck('S238 every tag and move is written in the stage log', (chr(35)+' STAGE-LOG v84.4') in _src and ('stage_log.json' in _src))"),
      ("'S239 a Finder move is repathed, not mourned", "'S238 every tag and move is written in the stage log", "ck('S239 a Finder move is repathed, not mourned', (chr(35)+' FINDER-MOVE v84.4') in _src)")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
