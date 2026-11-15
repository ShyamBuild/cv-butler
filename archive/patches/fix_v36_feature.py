import ast
done = []
p = 'briefing.py'; L = open(p).read().split('\n')
for k, l in enumerate(L):
    if "'brief','board')" in l and "'history'" not in l:
        L[k] = l.replace("'brief','board')", "'brief','board','history','stale')")
        done.append('cli-door-list'); break
if not any("startswith('history ')" in l for l in L):
    for k, l in enumerate(L):
        if 'briefing.do_missed(' in l:
            d = len(l) - len(l.lstrip())
            L.insert(k+1, d*' ' + "elif line.startswith('history '): briefing.do_history(raw[8:], root, print)")
            L.insert(k+2, d*' ' + "elif line.startswith('stale'): briefing.do_stale(raw[5:].strip(), root, print)")
            done.append('chat-routes-call-anchor'); break
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done or 'nothing missing')
