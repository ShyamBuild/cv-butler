import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# PULSE-START-LATE v81.15' not in src:
    starts = [k for k, l in enumerate(B) if 'Thread(target=_pulse_loop' in l]
    if starts:
        for k in starts:
            B[k] = None
        B = [l for l in B if l is not None]
        done.append(f'early-start-removed-x{len(starts)}')
    i = next(k for k, l in enumerate(B) if l.strip() == '_console_start()')
    d = ind(B[i])
    B.insert(i, d*' ' + "_th.Thread(target=_pulse_loop, daemon=True).start()  # PULSE-START-LATE v81.15: born after every name it closes over exists")
    done.append('late-start')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S122 exactly one late pulse start" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S121 the pulse thread owns its clock" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S122 exactly one late pulse start', _src.count('Thread(target=' + '_pulse_loop') == 1 and (chr(35)+' PULSE-START-LATE') in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S122-guard')
print('✅', done)
