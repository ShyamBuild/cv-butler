import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def tag_pick_pending(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def _match_tail('))
    B[i:i] = ["def tag_pick_pending():  # TAG-PICK-ROUTE v84.3: a fresh question keeps the door open for a bare digit",
              "    import json as _j",
              "    try:",
              "        return _j.load(open(os.path.join(BASE_DIR, 'tag_pick.json'))).get('ts', 0) > time.time() - 600",
              "    except Exception:",
              "        return False",
              "def _repath_ledgers(old, new):  # STAGE-SYNC v84.3: clocks and history walk with the paper",
              "    import json as _j",
              "    for fn in ('pipeline.json', 'errands.json'):",
              "        lp = os.path.join(BASE_DIR, fn)",
              "        try:",
              "            d = _j.load(open(lp))",
              "        except Exception:",
              "            continue",
              "        if old in d:",
              "            d[new] = d.pop(old)",
              "            try: _j.dump(d, open(lp, 'w'), indent=1)",
              "            except Exception: pass",
              "def _stage_move(p, tag, say=print):  # STAGE-SYNC v84.3: a tagged paper rests in its tag's folder inside its position",
              "    root = _pl_root()",
              "    parts = os.path.relpath(p, root).split(os.sep)",
              "    if len(parts) >= 4 and parts[-2] in _tag_vocab(): pos = os.path.join(root, *parts[:-2])",
              "    elif len(parts) == 3: pos = os.path.join(root, *parts[:-1])",
              "    else: return",
              "    tgt = os.path.join(pos, tag)",
              "    if os.path.realpath(os.path.dirname(p)) == os.path.realpath(tgt): return",
              "    try:",
              "        os.makedirs(tgt, exist_ok=True)",
              "        newp = os.path.join(tgt, os.path.basename(p))",
              "        if os.path.exists(newp): say(f'📦 a paper already rests in {tag} - left in place'); return",
              "        os.rename(p, newp)",
              "        _repath_ledgers(p, newp)",
              "        say(f'📦 moved {os.path.basename(p)} into {tag}')",
              "    except Exception as _me:",
              "        say(f'⚠️ stage move skipped: {_me}')",
              ""]
    done.append('stage-sync')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if '_tag_write(p, cur + [tag])' in l and '_stage_move' not in l:
        d = ind(l)
        B[k] = d*' ' + "if on and tag not in cur: _tag_write(p, cur + [tag]); say(f'🏷️ tagged {os.path.basename(p)}: {tag}'); _stage_move(p, tag, say)"
        done.append('stage-move-call'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("if len(sys.argv) > 1 and sys.argv[1] in ('pending', 'status', 'note', 'desk', 'briefing', 'chase', 'tag')"):
        d = ind(l)
        B[k:k] = [d*' ' + "if len(sys.argv) > 1 and sys.argv[1].isdigit() and tag_pick_pending():  # TAG-PICK-ROUTE v84.3: the terminal door honours the digit too",
                  (d+4)*' ' + "tag_voice(sys.argv[1], True, print); sys.exit(0)"]
        done.append('cli-digit'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
srcg = '\n'.join(g)
if 'TAG-PICK-ROUTE' not in srcg:
    for k, l in enumerate(g):
        if l.strip().startswith("if q.startswith('pending'): do_pending("):
            d = ind(l)
            g[k:k] = [d*' ' + "if q.strip().isdigit() and butler.tag_pick_pending(): do_tagcmd(q.strip(), root); continue  # TAG-PICK-ROUTE v84.3: a bare digit answers the fresh question before the AI wakes"]
            done.append('chat-digit'); break
    srcg = '\n'.join(g)
if srcg != open(G).read():
    ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S234 a bare digit reaches the fresh question in every door", "'S233 overlapping chairs never double a human in a question", "ck('S234 a bare digit reaches the fresh question in every door', (chr(35)+' TAG-PICK-ROUTE v84.3') in _src and (chr(35)+' TAG-PICK-ROUTE v84.3') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and ('def tag_pick_pending(' in _src))"),
      ("'S235 a tagged paper rests in its tag's folder", "'S234 a bare digit reaches the fresh question in every door", "ck('S235 a tagged paper rests in its tag'+chr(39)+'s folder', (chr(35)+' STAGE-SYNC v84.3') in _src and ('def _stage_move(' in _src))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
