import ast
B = open('butler.py').read().split('\n'); done = []
def ind(l): return len(l) - len(l.lstrip())
i = next(k for k, l in enumerate(B) if l.strip() == 'self.slog = StageLog(root)' and 'class Butler:' not in '\n'.join(B[:k]))
del B[i]; done.append('recursion-removed')
i = next(k for k, l in enumerate(B) if l.strip() == 'self.lock = threading.Lock()')
B.insert(i+1, ind(B[i])*' ' + 'self.slog = StageLog(root)')
done.append('slog-in-butler-init')
for k, l in enumerate(B):
    if 'B._reconcile_tags(hsay, B.sweep_dirs(n))' in l and k < B.index(next(x for x in B if 'B.scanning = False' in x)):
        B[k] = ind(l)*' ' + 'B._reconcile_tags(print)'; done.append('startup-reconcile-fixed'); break
for k, l in enumerate(B):
    if l.strip() == 'B._reconcile_tags(print)' and k > B.index(next(x for x in B if 'last_hb > 120' in x)):
        d = ind(l)
        B[k:k+1] = [d*' ' + 'B._reconcile_tags(hsay, B.sweep_dirs(n))',
                    d*' ' + 'try:',
                    (d+4)*' ' + 'import fitrank; fitrank.tick(B)',
                    (d+4)*' ' + 'import ledger; ledger.tick(B)',
                    d*' ' + 'except Exception:',
                    (d+4)*' ' + 'pass']
        done.append('heartbeat-ticks-scoped'); break
i = next(k for k, l in enumerate(B) if l.strip().startswith('def do_text('))
for k in range(i, min(i+60, len(B))):
    if 'fitrank.mark_called(hit)' in B[k]:
        B[k] = B[k].replace('fitrank.mark_called(hit)', 'fitrank.mark_called(os.path.join(folder, x))')
        done.append('dotext-mark-called'); break
if "'S35 heartbeat ticks" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S34 ledgers live" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S35 heartbeat ticks + scoped reconcile', 'fitrank.tick(B)' in _src.split('last_hb > 120')[1])")
    B.insert(i+2, d*' ' + "ck('S36 StageLog not self-recursive', 'self.slog = StageLog(root)' not in _src.split('class StageLog:')[1].split('class Butler:')[0])")
    done.append('S35-S36-guards')
new = '\n'.join(B); ast.parse(new); open('butler.py', 'w').write(new)
S = open('ship.sh').read()
if 'fitrank.py' not in S:
    S = S.replace('"$HOME/CV_Tool/requirements.txt"', '"$HOME/CV_Tool/requirements.txt" "$HOME/CV_Tool/fitrank.py" "$HOME/CV_Tool/ledger.py"')
    open('ship.sh', 'w').write(S); done.append('mirror-includes-new-modules')
print('✅', done)
