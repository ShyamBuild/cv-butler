import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# RETOUCH' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'if not add and cur: add = list(cur)')
    B[i] = B[i] + '  # RETOUCH v81.19: a re-applied tag is an event, even inside one poll window'
    done.append('retouch-marker-restored')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
