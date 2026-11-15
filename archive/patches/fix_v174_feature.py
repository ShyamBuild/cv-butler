import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if '# STALE-WINDOW-SWEEP v81.32' in l and 'os.system' in l and '# OWNER-AWARE' not in l:
        B[k] = ind(l)*' ' + "os.system(\"pkill -f 'ad_wait.py' 2>/dev/null; pgrep -f 'wa_warm.py' >/dev/null 2>&1 || pkill -f 'Google Chrome for Testing' 2>/dev/null\")  # STALE-WINDOW-SWEEP v81.32: zombies die, owned warm browser lives # OWNER-AWARE v81.38"
        done.append('owner-aware-sweep'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S143 only ownerless browsers are swept" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S142 stale field text is cleared before placement" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S143 only ownerless browsers are swept', (chr(35)+' OWNER-AWARE v81.38') in _src and 'wa_warm.py' in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S143-guard')
print('✅', done)
