import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
if not any(l.startswith('import butler') for l in g):
    i = next(k for k, l in enumerate(g) if l.startswith('import '))
    g.insert(i, 'import butler  # LISTEN v81.67: the REPL teaches through the butler\'s book (module scope: the loop lives here)')
    done.append('butler-import-at-top')
    srcg = '\n'.join(g); ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
if "'S177 the REPL can name the butler it teaches through" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S176 the gate shows every red line before the window" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S177 the REPL can name the butler it teaches through', any(x.startswith('import butler') for x in open(os.path.join(BASE_DIR, 'briefing.py')).read().split(chr(10))))")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S177-guard')
print('✅', done)
