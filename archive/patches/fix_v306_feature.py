import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def clients_cmd(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def client_cmd('))
    B[i:i] = ["def clients_cmd(arg, root, say=print):  # CLIENTS-LIST v84.24: the taught map and every anonymous folder, each with its teach-line ready",
              "    try: cm = json.load(open(CLIENTMAP_PATH))",
              "    except Exception: cm = {}",
              "    if cm:",
              "        say('🏢 taught clients:')",
              "        for k in sorted(cm): say(f'   {k} = {cm[k]}')",
              "    else:",
              "        say('🏢 no client taught yet')",
              "    pending = []",
              "    for client in sorted(os.listdir(root)):",
              "        cp = os.path.join(root, client)",
              "        if client.startswith('.') or not os.path.isdir(cp): continue",
              "        if client not in cm: pending.append(client)",
              "    if pending:",
              "        say('🏢 anonymous client folders - teach each once:')",
              "        for c in pending: say(f'   client {c} = <company>')",
              "    elif cm:",
              "        say('✅ every client folder under the root is taught')",
              ""]
    done.append('clients-list')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if "'missed', 'jd', 'nudge', 'refer')" in l and "'clients'" not in l:
        B[k] = l.replace("'refer')", "'refer', 'clients')")
        done.append('cli-clients-tuple'); break
for k, l in enumerate(B):
    if l.strip().startswith("elif _v in ('missed', 'jd', 'nudge', 'refer'):") and 'clients' not in '\n'.join(B[k:k+7]):
        d = ind(l)
        B.insert(k, d*' ' + "elif _v == 'clients': clients_cmd(' '.join(_a), _pl_root(), print)")
        done.append('cli-clients-branch'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
if 'clients_cmd' not in '\n'.join(g):
    for k, l in enumerate(g):
        if l.strip().startswith("if q.startswith('client '):"):
            d = ind(l)
            g.insert(k+1, d*' ' + "if q.strip() == 'clients': butler.clients_cmd('', root, say); continue  # CLIENTS-LIST v84.24")
            done.append('chat-clients'); break
    srcg = '\n'.join(g)
    if srcg != open(G).read():
        ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S282 the client ledger shows the taught and names the anonymous", "'S281 the keywords answer in the bare terminal too", "ck('S282 the client ledger shows the taught and names the anonymous', (chr(35)+' CLIENTS-LIST v84.24') in _src and ('def clients_cmd(' in _src))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
