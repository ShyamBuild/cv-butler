import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
srcg = '\n'.join(g)
if '# ONE-CLERK v81.72' not in srcg:
    i = next(k for k, l in enumerate(g) if l.startswith('def phones_of(path):'))
    d = ind(g[i])
    g[i] = d*' ' + "def _phones_of_local(path):  # ONE-CLERK v81.72: the old clerk, kept as last resort only"
    g[i:i] = [d*' ' + "def phones_of(path):  # ONE-CLERK v81.72: every voice asks the butler's clerk - taught book, email witness, OCR, confession, all of it",
              d*' ' + "    _lb = _phones_by_basename(path)",
              d*' ' + "    if _lb: return _lb",
              d*' ' + "    try:",
              d*' ' + "        _bp = butler.phones_of(path)",
              d*' ' + "        if _bp: return _bp",
              d*' ' + "    except Exception: pass",
              d*' ' + "    return _phones_of_local(path)",
              ""]
    done.append('one-clerk')
    srcg = '\n'.join(g); ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
if "'S178 every voice asks the same clerk" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S177 the REPL can name the butler it teaches through" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S178 every voice asks the same clerk', 'def _phones_of_local(' in _br and 'butler.phones_of(path)' in _br)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S178-guard')
print('✅', done)
