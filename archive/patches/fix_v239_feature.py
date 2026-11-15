import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
srcg = '\n'.join(g)
if '# PROVENANCE-AT-PICK v81.92 + CANDIDATE-FIRST v81.93' not in srcg:
    for k, l in enumerate(g):
        if '# CANDIDATE-FIRST v81.93' in l:
            g[k] = l.replace('# CANDIDATE-FIRST v81.93:', '# PROVENANCE-AT-PICK v81.92 + CANDIDATE-FIRST v81.93:')
            done.append('marker-inherited'); break
    srcg = '\n'.join(g); ast.parse(srcg); open(G, 'w').write(srcg)
W = os.path.join(os.getcwd(), 'wa.py')
w = open(W).read().split('\n')
srcw = '\n'.join(w)
if '# NO-FIELD-EXIT v81.94' not in srcw:
    k = next(i for i, l in enumerate(w) if 'there is no message field to paste into' in l)
    d = ind(w[k])
    w[k+1:k+1] = [d*' ' + "_r = input('   [x] discard this round · [q] close the window · [Enter] keep it open, then teach or re-pick: ').strip().lower()  # NO-FIELD-EXIT v81.94: a dead number ends the round with ONE menu; the paste-advice never speaks after a no-field confession",
                  d*' ' + "if _r == 'q':",
                  d*' ' + "    try: page.close()",
                  d*' ' + "except Exception: pass",
                  d*' ' + "return False"]
    done.append('no-field-exit')
    srcw = '\n'.join(w); ast.parse(srcw); open(W, 'w').write(srcw)
B = open('butler.py').read().split('\n')
if "'S200 a dead number ends the round with one menu" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S199 the paper's own witness picks the candidate's number" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S200 a dead number ends the round with one menu', (chr(35)+' NO-FIELD-EXIT v81.94') in open(os.path.join(BASE_DIR, 'wa.py')).read())")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S200-guard')
print('✅', done)
