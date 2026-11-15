import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
c0 = next(k for k, l in enumerate(B) if l.startswith('def calls_cmd('))
c1 = next(k for k in range(c0 + 1, len(B)) if B[k].startswith('def sheet_cmd('))
if 'FOLDER-TRUTH' not in '\n'.join(B[c0:c1]):
    B[c0:c1] = ["def calls_cmd(arg, root, say=print):  # CHAIR v84.10b (v84.30): FOLDER-TRUTH - the sheet maps the folders, not the tags",
                "    scopes = [desk_resolve(arg, root)] if arg else (desk_paths() or [root])",
                "    s0 = sheet_load(); sk = skips_load()",
                "    items = []; seen = set(); reopened = 0",
                "    for sc in scopes:",
                "        if not sc or not os.path.isdir(sc): continue",
                "        for dp, dn, fn in os.walk(sc):",
                "            if os.path.basename(dp) in _tag_vocab(): continue  # FOLDER-TRUTH v84.30: a stage folder's residents are already spoken for",
                "            for x in fn:",
                "                if not _is_desk_candidate(x): continue",
                "                p = os.path.join(dp, x); rp = os.path.realpath(p)",
                "                if rp in seen or rp in sk: continue",
                "                seen.add(rp)",
                "                row = next((i for i in s0.get('items', []) if os.path.realpath(i.get('p', '')) == rp), None)",
                "                if row and row.get('status') == 'waiting': continue",
                "                if row:",
                "                    row['status'] = 'waiting'; row['outcome'] = ''; reopened += 1; continue  # FOLDER-TRUTH v84.30: dragged out means to be contacted again",
                "                items.append({'p': p, 'name': os.path.splitext(x)[0], 'status': 'waiting', 'fp': _fp(p)})",
                "    kept = [i for i in s0.get('items', []) if i.get('status') != 'waiting']",
                "    s0['date'] = time.strftime('%Y-%m-%d'); s0['items'] = kept + [i for i in s0.get('items', []) if i.get('status') == 'waiting'] + items",
                "    sheet_save(s0)",
                "    say(f'📞 call sheet seeded: {len(items) + reopened} candidate(s) outside the stage folders' + (f' · reopened {reopened}' if reopened else ''))",
                "    if items or reopened: say('   type: up')",
                ""]
    done.append('calls-folder-truth')
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith('if _tags_of(p) or _name_key(os.path.basename(p)) in cov:'):
        B[k] = ind(l)*' ' + "if os.path.basename(os.path.dirname(p)) in _tag_vocab(): it['status'] = 'done'; it['outcome'] = 'covered elsewhere'; continue  # FOLDER-TRUTH v84.30" if 'it[' in l or True else l
        B[k] = ind(l)*' ' + ("if os.path.basename(os.path.dirname(p)) in _tag_vocab(): it['status'] = 'done'; it['outcome'] = 'covered elsewhere'; continue  # FOLDER-TRUTH v84.30" if l.strip().endswith('continue') and 'for it in' not in l else B[k])
        done.append('up-reconcile-folder'); break
for k, l in enumerate(B):
    if l.strip().startswith('if _tags_of(p) or _name_key(os.path.basename(p)) in cov:'):
        d = ind(l)
        B[k:k+2] = [d*' ' + "if os.path.basename(os.path.dirname(p)) in _tag_vocab():",
                    (d+4)*' ' + "it['status'] = 'done'; it['outcome'] = 'covered elsewhere'; continue  # FOLDER-TRUTH v84.30"]
        done.append('up-seat-folder'); break
for k, l in enumerate(B):
    if l.strip().startswith('if rq in known or rq in sk or _tags_of(q) or _name_key(x) in cov: continue'):
        B[k] = ind(l)*' ' + "if rq in known or rq in sk or os.path.basename(dp) in _tag_vocab(): continue  # FOLDER-TRUTH v84.30"
        done.append('up-scan-folder'); break
src = '\n'.join(B)
t0 = next(k for k, l in enumerate(B) if l.startswith('def tags_tidy('))
t1 = next(k for k in range(t0 + 1, len(B)) if B[k].startswith('def '))
seg = B[t0:t1]
if 'FOLDER-TRUTH' not in '\n'.join(seg):
    j = next(k for k in range(t0, t1) if B[k].strip().startswith('if not bad and not wrong:'))
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
              (d+16)*' ' + "say(f'🧭 {x} rests in {stage} but wears {st[0] if st else \"no stage\"} - tag it to its folder? y / n')",
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
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
for k, l in enumerate(B):
    if l.strip().startswith("elif _v in ('missed', 'jd', 'nudge', 'refer'):") and 'CHAIR-KEYWORD' not in '\n'.join(B[k:k+6]):
        d = ind(l)
        B[k+3] = (d+4)*' ' + "_kw = ' '.join(_a) or ((os.path.splitext(os.path.basename(sheet_current()['p']))[0]) if sheet_current() else '')  # CHAIR-KEYWORD v84.30: a bare keyword during a call speaks to the seated candidate"
        B[k+4] = (d+4)*' ' + "if _fn: _fn(_kw, _pl_root(), print)"
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
