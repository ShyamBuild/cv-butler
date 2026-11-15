import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# RC-FRESH v66' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'self._route(fp, say)')
    B.insert(i, ind(B[i])*' ' + "try: self.rc.pop(os.stat(fp).st_ino, None)  # RC-FRESH v66")
    B.insert(i+1, ind(B[i])*' ' + "except Exception: pass")
    done.append('rc-fresh')
src = '\n'.join(B)
if 'now - prev[1] < 600: continue  # HEAL-RETRY v65' in src:
    i = next(k for k, l in enumerate(B) if 'now - prev[1] < 600: continue  # HEAL-RETRY v65' in l)
    B[i] = B[i].replace('< 600:', '< 60:')
    done.append('heal-retry-60s')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
F = open('briefing.py').read().split('\n')
if 'def do_renwhy(' not in '\n'.join(F):
    i = next(k for k, l in enumerate(F) if l.strip().startswith('def do_clientname('))
    F[i:i] = ["def do_renwhy(arg, root, say=print):",
              "    import butler, fitrank",
              "    hits = _hits_for((arg or '').strip(), root)",
              "    if not hits: say(f'🤷 no CV matches {arg!r}'); return",
              "    p = hits[0]; b = butler.Butler(root); b._jload()",
              "    log = []",
              "    b.handle_pdf(p, log.append)",
              "    say(f'🔎 {os.path.relpath(p, root)}')",
              "    say(f'   handle_pdf said: {log if log else \"(silent = rename refused)\"}')",
              "    try:",
              "        ino = os.stat(p).st_ino",
              "        say(f'   rc={b.rc.get(ino)} rcn={getattr(b, \"rcn\", {}).get(ino)} journal={\"yes\" if b.journal.get(p) else \"no\"}')",
              "    except Exception: pass",
              "    t = fitrank._text(p)",
              "    say(f'   text head: {\" | \".join(t.split(chr(10))[:3])[:200]}')",
              ""]
    done.append('renwhy-command')
for k, l in enumerate(F):
    if "'tpltest','refer')" in l and "'renwhy'" not in l:
        F[k] = l.replace("'refer')", "'refer','renwhy')"); done.append('door-list'); break
for k, l in enumerate(F):
    if l.strip().startswith("elif cmd == 'refer'"):
        F.insert(k+1, ind(l)*' ' + "elif cmd == 'renwhy': do_renwhy(arg, root, print)")
        done.append('cli-renwhy'); break
for k, l in enumerate(F):
    if l.strip().startswith("if q.lower().startswith('refer ')"):
        F.insert(k+1, ind(l)*' ' + "if q.lower().startswith('renwhy '): do_renwhy(q[7:].strip(), root); continue")
        done.append('chat-renwhy'); break
new = '\n'.join(F); ast.parse(new); open('briefing.py', 'w').write(new)
B = open('butler.py').read().split('\n')
if "'S82 heal un-disarms rename breaker" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S80 one ack clock per send" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S82 heal un-disarms rename breaker', (chr(35)+' RC-FRESH') in _src and '< 60: continue  # HEAL-RETRY' in _src)")
    B.insert(i+2, d*' ' + "ck('S83 renwhy X-ray routed', 'def do_renwhy(' in _br and \"cmd == 'renwhy'\" in _br)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S82-S83-guards')
print('✅', done)
