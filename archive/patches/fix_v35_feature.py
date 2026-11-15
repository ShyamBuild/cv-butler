import ast
p = 'briefing.py'; L = open(p).read().split('\n'); done = []
if not any("startswith('history ')" in l for l in L):
    for k, l in enumerate(L):
        if 'do_missed(' in l and 'startswith' in l:
            d = len(l) - len(l.lstrip())
            L.insert(k+1, d*' ' + "elif line.startswith('history '): briefing.do_history(raw[8:], root, print)")
            L.insert(k+2, d*' ' + "elif line.startswith('stale'): briefing.do_stale(raw[5:].strip(), root, print)")
            done.append('chat-routes'); break
if 'stage transitions for one candidate' not in '\n'.join(L):
    for k, l in enumerate(L):
        if 'missed  <number>' in l and 'usage' not in l:
            d = len(l) - len(l.lstrip())
            L.insert(k+1, d*' ' + 'history <name>       .. stage transitions for one candidate')
            L.insert(k+2, d*' ' + 'stale [days]         .. candidates in current stage longer than N days (default 7)')
            done.append('help-card'); break
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done or 'nothing missing')
