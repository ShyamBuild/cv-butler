import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
C = os.path.join(os.getcwd(), 'cadence.py')
c = open(C).read().split('\n')
srcc = '\n'.join(c)
if 'ann_rest' not in srcc:
    for k, l in enumerate(c):
        if "d.setdefault('ack_min', 10)" in l:
            c[k] = l + "; d.setdefault('ann_rest', 4 * 3600)  # ANN-REST v82.1: the machine's own voice rests four hours unless the due-set changes"
            done.append('ann-rest-cfg'); break
    srcc = '\n'.join(c)
if '# ANN-REST v82.1: the machine' not in srcc:
    c = srcc.split('\n')
    for k, l in enumerate(c):
        if l.strip().startswith('if due: say(') and 'follow-up(s) due - type: due' in l:
            d = ind(l)
            c[k:k+1] = [d*' ' + "if due:  # ANN-REST v82.1: the machine's own voice rests unless the due-set changes or the rest elapses; the master's voices (due, outbox, ack) never rest",
                        (d+4)*' ' + "_key = f\"{len(due)}:{min(i.get('due') for i in due)}\"",
                        (d+4)*' ' + "_ann = d.setdefault('ann', {})",
                        (d+4)*' ' + "if _ann.get('key') != _key or now - _ann.get('ts', 0) >= _cfg().get('ann_rest', 4 * 3600):",
                        (d+8)*' ' + "say(f\"📬 {len(due)} follow-up(s) due - type: due  (approve via: outbox)\")",
                        (d+8)*' ' + "_ann['key'] = _key; _ann['ts'] = now"]
            done.append('ann-rest'); break
    srcc = '\n'.join(c)
if srcc != open(C).read():
    ast.parse(srcc); open(C, 'w').write(srcc)
B = open('butler.py').read().split('\n')
if "'S209 the machine's own voice rests, the master's never" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S208 the class keeps its methods" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S209 the machine'+chr(39)+'s own voice rests, the master'+chr(39)+'s never', (chr(35)+' ANN-REST v82.1') in open(os.path.join(BASE_DIR, 'cadence.py')).read() and ('ann_rest' in open(os.path.join(BASE_DIR, 'cadence.py')).read()) and ('show_outbox' in open(os.path.join(BASE_DIR, 'cadence.py')).read()))")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S209-guard')
print('✅', done)
