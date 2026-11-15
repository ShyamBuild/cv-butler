import ast
p = 'butler.py'; L = open(p).read().split('\n'); done = []
for i, l in enumerate(L):
    if "'git', '-C', BASE_DIR, 'rev-parse', '--short', 'HEAD'" in l:
        d = len(l) - len(l.lstrip())
        L[i] = d*' ' + "r = subprocess.run(['git', '-C', os.path.dirname(os.path.abspath(__file__)), 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True, timeout=5)"
        done.append('git-stamp-self-contained')
        break
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done or 'nothing missing')
