import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
idxs = [k for k, l in enumerate(B) if l.strip() == 'self.slog = StageLog(root)']
if idxs and 'class Butler:' not in '\n'.join(B[:idxs[0]]):
    del B[idxs[0]]; done.append('recursion-removed')
i = next(k for k, l in enumerate(B) if l.strip() == 'self.lock = threading.Lock()')
if not any(x.strip() == 'self.slog = StageLog(root)' for x in B[i:i+6]):
    B.insert(i+1, ind(B[i])*' ' + 'self.slog = StageLog(root)'); done.append('slog-in-butler-init')
print('stage1', done, flush=True)
for k, l in enumerate(B):
    if 'B._reconcile_tags(hsay, B.sweep_dirs(n))' in l and k < next(j for j, x in enumerate(B) if 'B.scanning = False' in x):
        B[k] = ind(l)*' ' + 'B._reconcile_tags(print)'; done.append('startup-reconcile-fixed'); break
hb = next(j for j, x in enumerate(B) if 'last_hb > 120' in x)
for k in range(hb, len(B)):
    if B[k].strip() == 'B._reconcile_tags(print)':
        d = ind(B[k])
        B[k:k+1] = [d*' ' + 'B._reconcile_tags(hsay, B.sweep_dirs(n))',
                    d*' ' + 'try:',
                    (d+4)*' ' + 'import fitrank; fitrank.tick(B)',
                    (d+4)*' ' + 'import ledger; ledger.tick(B)',
                    d*' ' + 'except Exception:',
                    (d+4)*' ' + 'pass']
        done.append('heartbeat-ticks-scoped'); break
print('stage2', done, flush=True)
if "'S35 heartbeat ticks" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S34 ledgers live" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S35 heartbeat ticks + scoped reconcile', ('fitrank.' + 'tick(B)') in _src.split('last_hb > 120')[1])")
    B.insert(i+2, d*' ' + "ck('S36 StageLog not self-recursive', 'self.slog = StageLog(root)' not in _src.split('class StageLog:')[1].split('class Butler:')[0])")
    done.append('S35-S36-guards')
new = '\n'.join(B); ast.parse(new); open('butler.py', 'w').write(new)
print('stage3 butler written', flush=True)
F = open('briefing.py').read().split('\n')
i = next(k for k, l in enumerate(F) if l.strip().startswith('def do_text('))
for k in range(i, min(i+60, len(F))):
    if 'fitrank.mark_called(hit)' in F[k]:
        F[k] = F[k].replace('fitrank.mark_called(hit)', 'fitrank.mark_called(os.path.join(folder, x))')
        done.append('dotext-mark-called'); break
new = '\n'.join(F); ast.parse(new); open('briefing.py', 'w').write(new)
print('stage4 briefing written', flush=True)
S = open('ship.sh').read()
if 'fitrank.py' not in S:
    S = S.replace('"$HOME/CV_Tool/requirements.txt"', '"$HOME/CV_Tool/requirements.txt" "$HOME/CV_Tool/fitrank.py" "$HOME/CV_Tool/ledger.py"')
    open('ship.sh', 'w').write(S); done.append('mirror-includes-new-modules')
print('✅', done)
