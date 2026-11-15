import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# LOOP-ARMOUR v76' not in src:
    i = next(k for k, l in enumerate(B) if "_last_poll', 0) > 8:" in l)
    d = ind(B[i])
    j = i
    while j < len(B) and not B[j].strip().startswith('B._heal((lambda'): j += 1
    block = B[i:j+1]
    B[i:j+1] = [d*' ' + 'try:  # LOOP-ARMOUR v76'] + [((ind(x) if x.strip() else d)+4)*' ' + x.strip() if x.strip() else x for x in block] + \
               [d*' ' + "    open(os.path.join(BASE_DIR, 'butler_alive.stamp'), 'w').write(str(_t.time()))"] + \
               [d*' ' + 'except Exception as _e:',
                d*' ' + "    print(f'⚠️ pulse skipped: {_e}', flush=True)"]
    done.append('pulse-armoured')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S98 pulse cannot kill the watcher" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S97 heal and drain read tags per call" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S98 pulse cannot kill the watcher', (chr(35)+' LOOP-ARMOUR') in _src and 'butler_alive.stamp' in _src and 'pulse skipped' in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S98-guard')
print('✅', done)
