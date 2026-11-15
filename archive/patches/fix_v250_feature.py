import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
C = os.path.join(os.getcwd(), 'cadence.py')
srcc = open(C).read()
if "_ann = d.setdefault('ann', {})" not in srcc:
    c = srcc.split('\n')
    for k, l in enumerate(c):
        if l.strip().startswith('if due: say(') and 'follow-up(s) due - type: due' in l:
            d = ind(l)
            c[k:k+1] = [d*' ' + "if due:  # ANN-REST-PROCESS v82.2: the machine's own voice rests unless the due-set changes or the rest elapses; the master's voices (due, outbox, ack) never rest",
                        (d+4)*' ' + "_key = f\"{len(due)}:{min(i.get('due') for i in due)}\"",
                        (d+4)*' ' + "_ann = d.setdefault('ann', {})",
                        (d+4)*' ' + "if _ann.get('key') != _key or now - _ann.get('ts', 0) >= _cfg().get('ann_rest', 4 * 3600):",
                        (d+8)*' ' + "say(f\"📬 {len(due)} follow-up(s) due - type: due  (approve via: outbox)\")",
                        (d+8)*' ' + "_ann['key'] = _key; _ann['ts'] = now"]
            done.append('ann-rest-process'); break
    srcc = '\n'.join(c); ast.parse(srcc); open(C, 'w').write(srcc)
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if "'S209 the machine'+" in l and 'ANN-REST v82.1' in l:
        d = ind(l)
        B[k] = d*' ' + "ck('S209 the machine'+chr(39)+'s own voice rests, the master'+chr(39)+'s never', (chr(35)+' ANN-REST v82.1') in open(os.path.join(BASE_DIR, 'cadence.py')).read() and ('ann_rest' in open(os.path.join(BASE_DIR, 'cadence.py')).read()) and (\"_ann = d.setdefault('ann', {})\" in open(os.path.join(BASE_DIR, 'cadence.py')).read()) and ('show_outbox' in open(os.path.join(BASE_DIR, 'cadence.py')).read()))  # S209 repinned v82.2: the witness demands the process-block itself, not merely the config default"
        done.append('S209-repinned'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
