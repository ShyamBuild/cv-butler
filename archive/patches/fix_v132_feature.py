import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
old = "            if not os.path.exists(fp) or _settling(fp): return"
if old in src if False else old in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l == old)
    B[i] = ind(B[i])*' ' + "if not os.path.exists(fp) or _settling(fp): say(f'⏭️ autodraft skip (moved or settling): {os.path.basename(fp)}'); return"
    done.append('skip-moved-visibility')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
F = open('briefing.py').read().split('\n')
if 'def do_adlog(' not in '\n'.join(F):
    i = next(k for k, l in enumerate(F) if l.strip().startswith('def do_renwhy('))
    F[i:i] = ["def do_adlog(arg, root, say=print):  # ADLOG v81.2 (read-only)",
              "    n = 10",
              "    try: n = max(1, int((arg or '').strip()))",
              "    except Exception: pass",
              "    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'butler_live.log')",
              "    try: lines = open(p, encoding='utf-8', errors='replace').read().splitlines()",
              "    except Exception: say('📭 no butler log yet'); return",
              "    hits = [x for x in lines if 'autodraft' in x.lower()][-n:]",
              "    if not hits: say('📭 no autodraft lines yet - tag a file and watch this space'); return",
              "    for x in hits: say(x)",
              ""]
    done.append('adlog-command')
for k, l in enumerate(F):
    if "'renwhy','name')" in l and "'adlog'" not in l:
        F[k] = l.replace("'name')", "'name','adlog')"); done.append('door-list'); break
for k, l in enumerate(F):
    if l.strip().startswith("elif cmd == 'name'"):
        F.insert(k+1, ind(l)*' ' + "elif cmd == 'adlog': do_adlog(arg, root, print)")
        done.append('cli-adlog'); break
for k, l in enumerate(F):
    if l.strip().startswith("if q.lower().startswith('name ')"):
        F.insert(k+1, ind(l)*' ' + "if q.lower().startswith('adlog'): do_adlog(q[5:].strip(), root); continue")
        done.append('chat-adlog'); break
new = '\n'.join(F); ast.parse(new); open('briefing.py', 'w').write(new)
B = open('butler.py').read().split('\n')
if "'S110 autodraft log reachable from chat" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S109 autodraft silence explains itself" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S110 autodraft log reachable from chat', 'def do_adlog(' in _br and \"cmd == 'adlog'\" in _br and (chr(35)+' ADLOG') in _br)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S110-guard')
print('✅', done)
