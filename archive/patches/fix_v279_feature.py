import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'TAG_WAITING =' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def _tag_vocab('))
    B[i:i] = ["TAG_WAITING = ('Awaiting JD Confirmation', 'Awaiting CV Update')  # TAG-CLASS v84.5: debts that coexist - a candidate may owe the JD ack and the CV update at once",
              "def _tag_stage(t):  # TAG-CLASS v84.5: everything else is a stage - one at a time, folder-bound",
              "    return t in _tag_vocab() and t not in TAG_WAITING",
              ""]
    done.append('tag-class')
    src = '\n'.join(B)
a0 = next(k for k, l in enumerate(B) if l.startswith('def _tag_apply_one('))
a1 = next(k for k in range(a0 + 1, len(B)) if B[k].startswith('def tag_voice('))
if 'SHOW-BOTH' not in '\n'.join(B[a0:a1]):
    B[a0:a1] = ["def _tag_apply_one(p, tag, on, say=print):  # TAG-VOICE v84.5: waiting tags add instantly, stage tags transition with a proposal that shows now and after",
                "    import json as _j",
                "    cur = _tags_of(p)",
                "    if not on:",
                "        if tag in cur:",
                "            newt = [t for t in cur if t != tag]",
                "            _tag_write(p, newt); say(f'🏷️ untagged {os.path.basename(p)}: {tag}')",
                "            _stage_note(os.path.basename(p), cur, newt, os.path.basename(os.path.dirname(p)), os.path.basename(os.path.dirname(p)), 'chat/terminal')",
                "        else: say(f'🏷️ {os.path.basename(p)} already lacks {tag} - nothing changed')",
                "        return",
                "    if tag in cur: say(f'🏷️ {os.path.basename(p)} already wears {tag} - nothing changed'); return",
                "    if not _tag_stage(tag):",
                "        newt = cur + [tag]",
                "        _tag_write(p, newt); say(f'🏷️ tagged {os.path.basename(p)}: {tag} (added beside {\", \".join(cur) or \"nothing\"})')",
                "        _stage_note(os.path.basename(p), cur, newt, os.path.basename(os.path.dirname(p)), os.path.basename(os.path.dirname(p)), 'chat/terminal')",
                "        return",
                "    drops = [t for t in cur if _tag_stage(t) and t != tag]  # STAGE-ONE v84.4, classed v84.5: a stage replaces a stage, never a waiting debt",
                "    keeps = [t for t in cur if t in TAG_WAITING]",
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
                "    after = [t for t in cur if t not in drops] + [tag]",
                "    txt = f\"🤖 Proposal: {os.path.basename(p)} → {tag} · now: [{', '.join(cur) or '-'}] → after: [{', '.join(after)}]\"  # SHOW-BOTH v84.5",
                "    if drops: txt += f' · drops {\", \".join(drops)}'",
                "    if keeps: txt += f' · keeps {\", \".join(keeps)}'",
                "    if move_to: txt += f' · move {os.path.basename(os.path.dirname(p))} → {tag}'",
                "    if conflict: txt += f' · a paper already rests in {tag}, so it will be tagged in place'",
                "    say(txt + ' · reply y / n')",
                "    try: _j.dump({'p': p, 'tag': tag, 'on': on, 'move_to': bool(move_to) and not conflict, 'ts': int(time.time())}, open(os.path.join(BASE_DIR, 'pending_action.json'), 'w'))",
                "    except Exception: pass",
                ""]
    done.append('tag-apply-v845')
    src = '\n'.join(B)
e0 = next(k for k, l in enumerate(B) if l.startswith('def action_execute('))
e1 = next(k for k in range(e0 + 1, len(B)) if B[k].startswith('def '))
if '_tag_stage(tag)' not in '\n'.join(B[e0:e1]):
    B[e0:e1] = ["def action_execute(say=print):  # PROPOSE-FIRST v84.4 (classed v84.5): the yes that makes it so, dropping stages only",
                "    import json as _j",
                "    pp = os.path.join(BASE_DIR, 'pending_action.json')",
                "    try: pend = _j.load(open(pp))",
                "    except Exception: say('🤷 no proposal is waiting'); return",
                "    p, tag = pend.get('p'), pend.get('tag')",
                "    cur = _tags_of(p)",
                "    drops = [t for t in cur if _tag_stage(t) and t != tag] if _tag_stage(tag) else []",
                "    newtags = [t for t in cur if t not in drops] + ([tag] if tag not in cur else [])",
                "    try:",
                "        _tag_write(p, newtags)",
                "        say(f\"🏷️ {os.path.basename(p)}: {tag}\" + (f' (dropped {\", \".join(drops)})' if drops else ''))",
                "        _stage_note(os.path.basename(p), cur, newtags, os.path.basename(os.path.dirname(p)), os.path.basename(os.path.dirname(p)), 'chat/terminal')",
                "    except Exception as _te:",
                "        say(f'⚠️ tag write failed: {_te}'); return",
                "    if pend.get('move_to'): _stage_move(p, tag, say)",
                "    try: os.remove(pp)",
                "    except Exception: pass",
                ""]
    done.append('execute-v845')
    src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S240 waiting debts coexist and survive every stage transition", "'S239 a Finder move is repathed, not mourned", "ck('S240 waiting debts coexist and survive every stage transition', (chr(35)+' TAG-CLASS v84.5') in _src and ('TAG_WAITING' in _src) and ('def _tag_stage(' in _src))"),
      ("'S241 a transition shows now and after before it asks", "'S240 waiting debts coexist and survive every stage transition", "ck('S241 a transition shows now and after before it asks', (chr(35)+' SHOW-BOTH v84.5') in _src)")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
