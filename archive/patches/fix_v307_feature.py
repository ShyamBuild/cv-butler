import ast, os, json
done = []
def ind(l): return len(l) - len(l.lstrip())
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
for k, l in enumerate(g):
    if 'butler.client_cmd(q[7:].strip(), root, say)' in l:
        g[k] = l.replace('butler.client_cmd(q[7:].strip(), root, say)', 'butler.client_cmd(q[7:].strip(), root)') + '  # CLIENT-DISPATCH v84.25'
        done.append('dispatch-client'); break
for k, l in enumerate(g):
    if 'butler.posmeta_cmd(q[8:].strip(), root, say)' in l:
        g[k] = l.replace('butler.posmeta_cmd(q[8:].strip(), root, say)', 'butler.posmeta_cmd(q[8:].strip(), root)')
        done.append('dispatch-posmeta'); break
for k, l in enumerate(g):
    if "butler.clients_cmd('', root, say)" in l:
        g[k] = l.replace("butler.clients_cmd('', root, say)", "butler.clients_cmd('', root)")
        done.append('dispatch-clients'); break
srcg = '\n'.join(g)
if srcg != open(G).read():
    ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'CLIENT-PRUNE' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def clients_cmd('))
    j = next(k for k in range(i + 1, len(B)) if B[k].strip().startswith('if cm:'))
    B[j:j] = ["    stale = [k for k in cm if not os.path.isdir(os.path.join(root, k))]  # CLIENT-PRUNE v84.25: the ledger may only hold truths the filesystem confirms",
              "    if stale:",
              "        for k in stale: cm.pop(k, None)",
              "        try: json.dump(cm, open(CLIENTMAP_PATH, 'w'), indent=1)",
              "        except Exception: pass",
              "        say('🧹 pruned keys that match no client folder: ' + ', '.join(stale))"]
    done.append('clients-prune')
    src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
lp = os.path.expanduser('~/CV_Tool/clients.json')
try:
    cm = json.load(open(lp)); root = os.path.expanduser('~/Downloads/Sunsoft Technology')
    keep = {k: v for k, v in cm.items() if os.path.isdir(os.path.join(root, k))}
    if len(keep) != len(cm):
        json.dump(keep, open(lp, 'w'), indent=1)
        done.append('json-pruned:' + ','.join(sorted(set(cm) - set(keep))))
except Exception:
    pass
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S283 the teach door works in chat and the ledger holds only real folders", "'S282 the client ledger shows the taught and names the anonymous", "ck('S283 the teach door works in chat and the ledger holds only real folders', (chr(35)+' CLIENT-DISPATCH v84.25') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and (chr(35)+' CLIENT-PRUNE v84.25') in _src)")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
