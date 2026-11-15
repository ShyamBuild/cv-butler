import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
c0 = next(k for k, l in enumerate(B) if l.startswith('def calls_cmd('))
c1 = next(k for k in range(c0 + 1, len(B)) if B[k].startswith('def sheet_cmd('))
if 'FOLDER-TRUTH' not in '\n'.join(B[c0:c1]):
    B[c0:c1] = ["def calls_cmd(arg, root, say=print):  # CHAIR v84.10b (v84.30): FOLDER-TRUTH - the sheet maps the folders, not the tags",
                "    scopes = [desk_resolve(arg, root)] if arg else (desk_paths() or [root])",
                "    s0 = sheet_load(); sk = skips_load(); mem = set(covered_load())",
                "    items = []; seen = set(); reopened = 0",
                "    for sc in scopes:",
                "        if not sc or not os.path.isdir(sc): continue",
                "        for dp, dn, fn in os.walk(sc):",
                "            if os.path.basename(dp) in _tag_vocab(): continue  # FOLDER-TRUTH v84.30: a stage folder's residents are already spoken for",
                "            for x in fn:",
                "                if not _is_desk_candidate(x): continue",
                "                p = os.path.join(dp, x); rp = os.path.realpath(p)",
                "                if rp in seen or rp in sk or _name_key(x) in mem: continue",
                "                seen.add(rp)",
                "                row = next((i for i in s0.get('items', []) if os.path.realpath(i.get('p', '')) == rp), None)",
                "                if row and row.get('status') == 'waiting': continue",
                "                if row:",
                "                    row['status'] = 'waiting'; row['outcome'] = ''; reopened += 1; continue  # FOLDER-TRUTH v84.30: dragged out means to be contacted again",
                "                items.append({'p': p, 'name': os.path.splitext(x)[0], 'status': 'waiting', 'fp': _fp(p)})",
                "    waiting = [i for i in s0.get('items', []) if i.get('status') == 'waiting']",
                "    kept = [i for i in s0.get('items', []) if i.get('status') != 'waiting']",
                "    s0['date'] = time.strftime('%Y-%m-%d'); s0['items'] = kept + waiting + items",
                "    sheet_save(s0)",
                "    say(f'📞 call sheet seeded: {len(items) + reopened} candidate(s) outside the stage folders' + (f' · reopened {reopened}' if reopened else ''))",
                "    if items or reopened: say('   type: up')",
                ""]
    done.append('calls-folder-truth')
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith('cov = _covered_names(root)') and 'def up_cmd' in '\n'.join(B[max(0, k-8):k]):
        B[k] = ind(l)*' ' + "mem = set(covered_load())  # FOLDER-TRUTH v84.30: outcome memory guards duplicates; the folders decide the rest"
        done.append('up-mem'); break
hits = [k for k, l in enumerate(B) if l.strip().startswith('if _tags_of(p) or _name_key(os.path.basename(p)) in cov:')]
for k in reversed(hits):
    d = ind(B[k])
    B[k:k+1] = [d*' ' + "if os.path.basename(os.path.dirname(p)) in _tag_vocab() or _name_key(os.path.basename(p)) in mem:",
                (d+4)*' ' + "it['status'] = 'done'; it['outcome'] = 'covered elsewhere'; continue  # FOLDER-TRUTH v84.30"]
if hits: done.append('up-folder-conditions-x%d' % len(hits))
for k, l in enumerate(B):
    if l.strip().startswith('if rq in known or rq in sk or _tags_of(q) or _name_key(x) in cov: continue'):
        B[k] = ind(l)*' ' + "if rq in known or rq in sk or os.path.basename(dp) in _tag_vocab() or _name_key(x) in mem: continue  # FOLDER-TRUTH v84.30"
        done.append('up-scan-folder'); break
src = '\n'.join(B)
t0 = next(k for k, l in enumerate(B) if l.startswith('def tags_tidy('))
t1 = next(k for k in range(t0 + 1, len(B)) if B[k].startswith('def '))
if 'FOLDER-TRUTH' not in '\n'.join(B[t0:t1]):
    j = next(k for k in range(t0, t1) if B[k].strip().startswith('if moved: say('))
    d = ind(B[j])
    B[j:j] = [d*' ' + "seen2 = set()",
              d*' ' + "for sc in desk_paths():  # FOLDER-TRUTH v84.30: where folder and tag disagree, tidy asks - one keystroke each way",
              (d+4)*' ' + "for dp, dn, fn in os.walk(sc):",
              (d+8)*' ' + "stage = os.path.basename(dp)",
              (d+8)*' ' + "for x in fn:",
              (d+12)*' ' + "if not _is_desk_candidate(x): continue",
              (d+12)*' ' + "p = os.path.join(dp, x); rp = os.path.realpath(p)",
              (d+12)*' ' + "if rp in seen2: continue",
              (d+12)*' ' + "seen2.add(rp)",
              (d+12)*' ' + "tgs = _tags_of(p); st = [t for t in tgs if _tag_stage(t)]",
              (d+12)*' ' + "if stage in _tag_vocab() and (not st or st[0] != stage):",
              (d+16)*' ' + "say(f'🧭 {x} rests in {stage} but wears {st[0] if st else chr(34)+chr(34)} - tag it to its folder? y / n')",
              (d+16)*' ' + "if confirm_wait(say) == 'y':",
              (d+20)*' ' + "newt = [t for t in tgs if not _tag_stage(t)] + [stage]",
              (d+20)*' ' + "_tag_write(p, newt); _stage_note(x, tgs, newt, stage, stage, 'tidy-folder')",
              (d+20)*' ' + "say(f'🏷️ {x}: {stage}')",
              (d+12)*' ' + "elif stage not in _tag_vocab() and st:",
              (d+16)*' ' + "say(f'🧭 {x} wears {st[0]} but rests outside the stage folders - untag it back to the contact list? y / n')",
              (d+16)*' ' + "if confirm_wait(say) == 'y':",
              (d+20)*' ' + "newt = [t for t in tgs if t != st[0]]",
              (d+20)*' ' + "_tag_write(p, newt); _stage_note(x, tgs, newt, stage, stage, 'tidy-folder')",
              (d+20)*' ' + "say(f'🏷️ untagged {x}: {st[0]} - back to the contact list')",
              ]
    done.append('tidy-folder-truth')
src = '\n'.join(B)
for k, l in enumerate(B):
    if "ck('S260 covered means any tag" in l:
        d = ind(l)
        B[k] = d*' ' + "ck('S260 covered means filed, remembered or skipped - the sheet seats only the loose', (chr(35)+' FOLDER-TRUTH v84.30') in _src and ('skips_load(); mem = set(covered_load())' in _src))  # S260 repinned v84.30: coverage grew a better definition - the folder, the memory, the skip"
        done.append('S260-repinned'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if l.strip().startswith("elif _v in ('missed', 'jd', 'nudge', 'refer'):") and 'CHAIR-KEYWORD' not in '\n'.join(B[k:k+8]):
        d = ind(l); d4 = (d+4)*' '
        B[k+3:k+5] = [d4 + "_kw = ' '.join(_a) or ((os.path.splitext(os.path.basename(sheet_current()['p']))[0]) if sheet_current() else '')  # CHAIR-KEYWORD v84.30: a bare keyword during a call speaks to the seated candidate",
                      d4 + "if _fn: _fn(_kw, _pl_root(), print)",
                      d4 + "else: print('🤷 voice missing: ' + _v)"]
        done.append('cli-chair-keyword'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
if 'CHAIR-KEYWORD' not in '\n'.join(g):
    for k, l in enumerate(g):
        if 'butler.sheet_current() and q.strip() in (' in l and 'do_outcome' in l:
            d = ind(l)
            g.insert(k, d*' ' + "if butler.sheet_current() and q.strip() in ('jd', 'missed', 'nudge', 'refer'): q = q + ' ' + os.path.splitext(os.path.basename(butler.sheet_current()['p']))[0]  # CHAIR-KEYWORD v84.30")
            done.append('chat-chair-keyword'); break
    srcg = '\n'.join(g)
    if srcg != open(G).read():
        ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S288 the sheet maps the folders - dragged out means to be contacted again", "'S287 the designation slot is never blank and the city list holds no twins", "ck('S288 the sheet maps the folders - dragged out means to be contacted again', (chr(35)+' FOLDER-TRUTH v84.30') in _src)"),
      ("'S289 a bare keyword during a call speaks to the seated candidate", "'S288 the sheet maps the folders - dragged out means to be contacted again", "ck('S289 a bare keyword during a call speaks to the seated candidate', (chr(35)+' CHAIR-KEYWORD v84.30') in _src and (chr(35)+' CHAIR-KEYWORD v84.30') in open(os.path.join(BASE_DIR, 'briefing.py')).read())")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
