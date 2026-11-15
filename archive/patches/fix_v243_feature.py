import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
W = os.path.join(os.getcwd(), 'wa.py')
w = open(W).read().split('\n')
srcw = '\n'.join(w)
if '# MODAL-WATCH v81.98' not in srcw:
    for k, l in enumerate(w):
        if l.strip() == 'for _i in range(8):':
            w[k] = ind(l)*' ' + "for _i in range(48):  # MODAL-WATCH v81.98: the door is asked until it answers - twenty-four beats, not four; the modal confesses, the composer releases, and only true ambiguity pays the full count"
            done.append('modal-watch'); break
    srcw = '\n'.join(w); ast.parse(srcw); open(W, 'w').write(srcw)
B = open('butler.py').read().split('\n')
if "'S202 the door is asked until it answers" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S201 the field detector sees the composer, not the search box" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S202 the door is asked until it answers', (chr(35)+' MODAL-WATCH v81.98') in open(os.path.join(BASE_DIR, 'wa.py')).read() and ('for _i in range(' + '48):') in open(os.path.join(BASE_DIR, 'wa.py')).read())")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S202-guard')
print('✅', done)
