import ast
p = 'briefing.py'; L = open(p).read().split('\n'); done = []
if not any("startswith('history" in l for l in L):
    for k, l in enumerate(L):
        if 'do_missed(q[6:], root)' in l:
            d = (len(l) - len(l.lstrip())) - 4
            L.insert(k+1, d*' ' + "if q.lower().startswith('history '): do_history(q[8:], root); continue")
            L.insert(k+2, d*' ' + "if q.lower().startswith('history'): do_history(q[7:].strip(), root); continue")
            L.insert(k+3, d*' ' + "if q.lower().startswith('stale'): do_stale(q[5:].strip(), root); continue")
            done.append('chat-routes-exact'); break
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done or 'nothing missing')
