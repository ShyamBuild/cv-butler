import ast
p = 'butler.py'; L = open(p).read().split('\n')
src = '\n'.join(L)
absent = [f'S{n}' for n in range(1, 20) if f"ck('S{n} " not in src]
print('absent skill labels in source:', absent or 'none')
done = []
if absent == ['S12']:
    for k, l in enumerate(L):
        if "ck('S16 send phase launches+fills'" in l:
            L[k] = l.replace("ck('S16 send phase launches+fills'", "ck('S12 send phase launches+fills'")
            done.append('S12-label-restored')
            break
    src = '\n'.join(L)
    ast.parse(src); open(p, 'w').write(src)
print('✅', done or 'nothing missing')
