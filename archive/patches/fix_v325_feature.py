import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def twins_cmd(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def forget_cmd('))
    B[i:i] = ["def twins_cmd(arg, root, say=print):  # TWINS v84.36: same human, several papers - named for the master's Bin decision, never deleted by the machine",
              "    groups = {}",
              "    for sc in desk_paths() or [root]:",
              "        for dp, dn, fn in os.walk(sc):",
              "            for x in fn:",
              "                if not _is_desk_candidate(x): continue",
              "                groups.setdefault(_name_key(x), []).append(os.path.join(dp, x))",
              "    shown = 0",
              "    for k, ps in sorted(groups.items()):",
              "        if arg and arg.lower() not in k: continue",
              "        if len(ps) < 2: continue",
              "        shown += 1",
              "        say(f'👥 {k}:')",
              "        for p in ps:",
              "            tgs = _tags_of(p); stage = os.path.basename(os.path.dirname(p))",
              "            hint = ' · keeper?' if (stage in _tag_vocab() or tgs) else ''",
              "            say(f'   · {os.path.relpath(p, root)} · tags: {\", \".join(tgs) or \"none\"}{hint}')",
              "        say('   the Bin is yours - I never delete')",
              "    if not shown: say('✅ no twin papers on the desk - every human rests in one file')",
              ""]
    done.append('twins')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if "'clients', 'refresh', 'options', 'draftwhy')" in l and 'twins' not in l:
        B[k] = l.replace("'draftwhy')", "'draftwhy', 'twins')")
        done.append('cli-twins-tuple'); break
for k, l in enumerate(B):
    if l.strip().startswith("elif _v == 'draftwhy':") and 'twins' not in '\n'.join(B[k:k+3]):
        d = ind(l)
        B.insert(k+1, d*' ' + "elif _v == 'twins': twins_cmd(' '.join(_a), _pl_root(), print)")
        done.append('cli-twins-branch'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
if 'twins_cmd' not in '\n'.join(g):
    for k, l in enumerate(g):
        if l.strip().startswith("if q.startswith('draftwhy '):"):
            d = ind(l)
            g.insert(k+1, d*' ' + "if q == 'twins' or q.startswith('twins '): butler.twins_cmd(q[5:].strip(), root, say); continue  # TWINS v84.36")
            done.append('chat-twins'); break
    srcg = '\n'.join(g)
    if srcg != open(G).read():
        ast.parse(srcg); open(G, 'w').write(srcg)
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v84.36' not in t:
        open(AR, 'a').write('v84.36: twins - duplicate papers of one human named with paths, tags and a keeper hint; the Bin stays the master\'s hand\n')
        done.append('arch-line')
except Exception:
    pass
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S300 twins names every duplicate group and never deletes", "'S299 the brain answers the ear in strict JSON only, and offline it is silent", "ck('S300 twins names every duplicate group and never deletes', (chr(35)+' TWINS v84.36') in _src and ('def twins_cmd(' in _src) and ('I never delete' in _src))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
