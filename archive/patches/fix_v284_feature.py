import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if l.strip().startswith('after = [t for t in cur if t not in drops] + [tag]'):
        d = ind(l)
        B[k] = d*' ' + "after = [t for t in cur if t not in drops] + ([tag] if tag not in cur else [])  # AFTER-ONCE v84.9: a proposal may not stutter"
        done.append('after-once'); break
src = '\n'.join(B)
a0 = next(k for k, l in enumerate(B) if l.startswith('def tags_audit('))
a1 = next(k for k in range(a0 + 1, len(B)) if B[k].startswith('def '))
if 'TIDY v84.9' not in '\n'.join(B[a0:a1]):
    B[a0:a1] = ["def tags_audit(say=print):  # AUDIT v84.7 (v84.9): two stages, or a stage away from its folder - named, never silently rewritten",
                "    seen = set(); bad = 0; wrong = []",
                "    for sc in desk_paths():",
                "        for dp, dn, fn in os.walk(sc):",
                "            for x in fn:",
                "                if not x.lower().endswith(('.pdf', '.docx')): continue",
                "                p = os.path.join(dp, x); rp = os.path.realpath(p)",
                "                if rp in seen: continue",
                "                seen.add(rp)",
                "                tgs = _tags_of(p); st = [t for t in tgs if _tag_stage(t)]",
                "                par = os.path.basename(dp)",
                "                if len(st) > 1:",
                "                    bad += 1",
                "                    say(f'⚠️ {x} · in {par} · wears {\", \".join(st)} - one transition will settle it')",
                "                elif len(st) == 1 and par in _tag_vocab() and par != st[0]:",
                "                    wrong.append((x, par, st[0]))",
                "    for x, par, stg in wrong:",
                "        say(f'🧭 {x} · rests in {par} · wears {stg} - tidy will carry it home')",
                "    if not bad and not wrong: say('✅ every paper on the desk rests in exactly one stage, in its own folder')",
                "def tags_tidy(say=print):  # TIDY v84.9: carry each misplaced paper home, one keystroke at a time; twins stand down until the master Bins",
                "    seen = set(); moved = 0; held = 0",
                "    for sc in desk_paths():",
                "        for dp, dn, fn in os.walk(sc):",
                "            for x in fn:",
                "                if not x.lower().endswith(('.pdf', '.docx')): continue",
                "                p = os.path.join(dp, x); rp = os.path.realpath(p)",
                "                if rp in seen: continue",
                "                seen.add(rp)",
                "                st = [t for t in _tags_of(p) if _tag_stage(t)]",
                "                par = os.path.basename(dp)",
                "                if not (len(st) == 1 and par in _tag_vocab() and par != st[0]): continue",
                "                tgt = os.path.join(os.path.dirname(dp), st[0]); twin = os.path.join(tgt, x)",
                "                if os.path.exists(twin):",
                "                    say(f'🧭 {x} · {par} → {st[0]} · a twin rests there ({os.path.relpath(twin, _pl_root())}) - Bin one first; standing down')",
                "                    held += 1; continue",
                "                say(f'🧭 Proposal: move {x} · {par} → {st[0]} · y / n')",
                "                k = confirm_wait(say)",
                "                if k == 'y':",
                "                    try:",
                "                        os.makedirs(tgt, exist_ok=True)",
                "                        os.rename(p, twin)",
                "                        _repath_ledgers(p, twin)",
                "                        _stage_note(x, st[0], st[0], par, st[0], 'chat/terminal')",
                "                        say(f'📦 moved {x} into {st[0]}'); moved += 1",
                "                    except Exception as _me:",
                "                        say(f'⚠️ move skipped: {_me}')",
                "                else:",
                "                    say('· left in place')",
                "    if moved: say(f'🧺 carried {moved} paper(s) home')",
                "    elif held: say('🧺 nothing moved - twins wait for your Bin')",
                "    else: say('🧺 every paper rests where its tag says')",
                ""]
    done.append('audit-tidy')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if "'chase', 'tag', 'dash', 'audit')" in l:
        B[k] = l.replace("'chase', 'tag', 'dash', 'audit')", "'chase', 'tag', 'dash', 'audit', 'tidy')")
        if 'cli-tidy' not in done: done.append('cli-tidy')
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("elif _v == 'audit':"):
        d = ind(l)
        B.insert(k+1, d*' ' + "elif _v == 'tidy': tags_tidy(print)")
        done.append('cli-tidy-branch'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
srcg = '\n'.join(g)
if 'def do_tidy(' not in srcg:
    i = next(k for k, l in enumerate(g) if l.startswith('def do_audit('))
    g[i:i] = ["def do_tidy(arg, root, say=print):  # TIDY v84.9",
              "    butler.tags_tidy(say)",
              ""]
    done.append('chat-tidy-fn')
    srcg = '\n'.join(g)
if not any(l.strip().startswith("if q.startswith('tidy')") for l in g):
    for k, l in enumerate(g):
        if l.strip().startswith("if q.startswith('audit'): do_audit("):
            d = ind(l)
            g.insert(k+1, d*' ' + "if q.startswith('tidy'): do_tidy(q[4:].strip(), root); continue  # TIDY v84.9")
            done.append('chat-tidy-dispatch'); break
    srcg = '\n'.join(g)
if srcg != open(G).read():
    ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S248 a proposal tells its after-set once", "'S247 a name-conflict names the twin and never deletes it", "ck('S248 a proposal tells its after-set once', (chr(35)+' AFTER-ONCE v84.9') in _src)"),
      ("'S249 a paper away from its stage's folder is named by audit and moved only by tidy's keystroke", "'S248 a proposal tells its after-set once", "ck('S249 a paper away from its stage'+chr(39)+'s folder is named by audit and moved only by tidy'+chr(39)+'s keystroke', (chr(35)+' TIDY v84.9') in _src and ('def tags_tidy(' in _src))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
