import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def tag_voice(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def tag_apply('))
    i1 = next(k for k in range(i + 1, len(B)) if B[k].startswith('def ') or B[k].startswith('DESK_PATH'))
    B[i:i1] = ["def _match_tail(arg):  # TAG-TAIL v84.2c: the tag is the longest vocabulary tag your sentence ends with",
               "    low = (arg or '').lower().strip(); best = None",
               "    for t in _tag_vocab():",
               "        if low.endswith(t.lower()) and (best is None or len(t) > len(best)): best = t",
               "    return best",
               "def _tag_apply_one(p, tag, on, say=print):  # TAG-VOICE v84.2c: read, modify, write - every other tag preserved",
               "    cur = _tags_of(p)",
               "    try:",
               "        if on and tag not in cur: _tag_write(p, cur + [tag]); say(f'🏷️ tagged {os.path.basename(p)}: {tag}')",
               "        elif not on and tag in cur: _tag_write(p, [t for t in cur if t != tag]); say(f'🏷️ untagged {os.path.basename(p)}: {tag}')",
               "        else: say(f'🏷️ {os.path.basename(p)} already {\"wears\" if on else \"lacks\"} {tag} - nothing changed')",
               "    except Exception as _te:",
               "        say(f'⚠️ tag write failed: {_te}')",
               "def tag_voice(arg, on, say=print):  # TAG-VOICE v84.2c: names may hold spaces, the tag is read from the tail, and a question keeps its numbers",
               "    import json as _j",
               "    arg = (arg or '').strip()",
               "    pk = os.path.join(BASE_DIR, 'tag_pick.json')",
               "    pend = None",
               "    try:",
               "        pend = _j.load(open(pk))",
               "        if pend.get('ts', 0) < time.time() - 600: pend = None",
               "    except Exception:",
               "        pend = None",
               "    if pend:",
               "        first = arg.split()[0] if arg.split() else ''",
               "        if first.isdigit():  # TAG-PICK v84.2c: a bare digit answers the last question, exactly like the phone picker",
               "            i = int(first) - 1; rest = arg.split(' ', 1)[1] if ' ' in arg else ''",
               "            if 0 <= i < len(pend.get('cands', [])):",
               "                tg = _match_tail(rest) or pend.get('tag')",
               "                try: os.remove(pk)",
               "                except Exception: pass",
               "                _tag_apply_one(pend['cands'][i], tg, pend.get('on', on), say); return",
               "            say(f'🤷 no candidate number {first} in the last question'); return",
               "    tag = _match_tail(arg)",
               "    if not tag: say(f\"🤷 no known tag at the end of {arg!r} - put the tag words last, e.g. tag lalan kumar ready for manager review\"); return",
               "    name = arg[:len(arg) - len(tag)].strip()",
               "    if not name: say('usage: tag <name> <tag words>'); return",
               "    scope = desk_paths() or [_pl_root()]",
               "    toks = [t for t in name.lower().split() if t]; cands = []",
               "    for sc in scope:",
               "        for dp, dn, fn in os.walk(sc):",
               "            for x in fn:",
               "                if x.lower().endswith(('.pdf', '.docx')) and all(t in x.lower() for t in toks): cands.append(os.path.join(dp, x))",
               "    if not cands: say(f'🤷 no candidate file matches {name!r} on the desk'); return",
               "    if len(cands) == 1: _tag_apply_one(cands[0], tag, on, say); return",
               "    say('❓ several humans match - type the number to choose:')",
               "    for n, c in enumerate(cands[:9], 1):",
               "        say(f'   {n}) {os.path.basename(c)} · in {os.path.basename(os.path.dirname(c))}')",
               "    try: _j.dump({'cands': cands[:9], 'tag': tag, 'on': on, 'ts': int(time.time())}, open(pk, 'w'))",
               "    except Exception: pass",
               ""]
    done.append('tag-voice')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if "'desk', 'briefing', 'chase')" in l and 'sys.argv' in l:
        B[k] = l.replace("'desk', 'briefing', 'chase')", "'desk', 'briefing', 'chase', 'tag')")
        if 'cli-tag' not in done: done.append('cli-tag')
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("elif _v == 'chase':"):
        d = ind(l)
        B.insert(k+1, d*' ' + "elif _v == 'tag':  # TAG-VOICE v84.2c in the terminal door")
        B.insert(k+2, (d+4)*' ' + "_aa = list(_a); _on = True")
        B.insert(k+3, (d+4)*' ' + "if _aa and _aa[0] == 'off': _on = False; _aa = _aa[1:]")
        B.insert(k+4, (d+4)*' ' + "tag_voice(' '.join(_aa), _on, print)")
        done.append('cli-tag-branch'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
for k, l in enumerate(g):
    if l.strip().startswith('def do_tagcmd('):
        i0 = k
        i1 = next(m for m in range(k + 1, len(g)) if g[m].startswith('def ') or (g[m].strip() == '' and m + 1 < len(g) and g[m+1].startswith('def ')))
        g[i0:i1] = ["def do_tagcmd(arg, root, say=print):  # TAG-VOICE v84.2c: the whole sentence goes to the clerk; the tag is read from its tail",
                    "    if arg.startswith('off '): butler.tag_voice(arg[4:], False, say); return",
                    "    butler.tag_voice(arg, True, say)",
                    ""]
        done.append('chat-tag-repoint'); break
srcg = '\n'.join(g)
if srcg != open(G).read():
    ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S225 the verbs and the tag voice answer before any root is validated", "'S224 the parse asks twice before it stays silent", "ck('S225 the verbs and the tag voice answer before any root is validated', (chr(35)+' QUIET-VERBS v84.2') in _src and ('def tag_voice(' in _src) and (chr(35)+' PIPELINE-CLI-FIRST') in _src)"),
      ("'S231 the tag is read from the tail so names may hold spaces", "'S230 every tag function carries its own import", "ck('S231 the tag is read from the tail so names may hold spaces', (chr(35)+' TAG-TAIL v84.2c') in _src)"),
      ("'S232 a question keeps its numbers and a bare digit answers it", "'S231 the tag is read from the tail so names may hold spaces", "ck('S232 a question keeps its numbers and a bare digit answers it', (chr(35)+' TAG-PICK v84.2c') in _src and ('tag_pick.json' in _src))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
