import ast
rep = {f: open(f).read().split('\n') for f in ('briefing.py', 'butler.py')}
done = []
L = rep['briefing.py']
if not any("startswith('history ')" in l for l in L):
    for k, l in enumerate(L):
        if 'do_missed(raw' in l and 'startswith' in l:
            d = len(l) - len(l.lstrip())
            L.insert(k+1, d*' ' + "elif line.startswith('history '): do_history(raw[8:], root, print)")
            L.insert(k+2, d*' ' + "elif line.startswith('stale'): do_stale(raw[5:].strip(), root, print)")
            done.append('chat-routes-bare'); break
rep['briefing.py'] = L
B = rep['butler.py']
for k, l in enumerate(B):
    if 'B.route(tmp, print)' in l:
        B[k] = l.replace('B.route(tmp, print)', 'B.route(tmp, lambda _m: None)')
        done.append('S4-quiet-route'); break
rep['butler.py'] = B
for f in rep:
    open(f, 'w').write('\n'.join(rep[f]))
print('✅', done or 'nothing missing')
