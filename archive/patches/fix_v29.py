import ast
p = 'butler.py'; L = open(p).read().split('\n'); done = []
if 'cands = [f for f in sorted' not in '\n'.join(L):
    i = next(k for k, l in enumerate(L) if 'zz_garbage_test.pdf' in l and 'tmp =' in l)
    a = i
    j = next(k for k in range(i, len(L)) if 'os.remove(os.path.join(root, f))' in L[k])
    d = len(L[a]) - len(L[a].lstrip())
    L[a:j+1] = [d*' ' + "cands = [f for f in sorted(os.listdir(root)) if f.lower().endswith('.pdf') and not f.startswith('zz_')",
                d*' ' + "         and not f.lower().startswith('jd') and ' jd' not in f.lower() and '_jd' not in f.lower()",
                d*' ' + "         and not f.lower().startswith('regional') and 'location' not in f.lower()]",
                d*' ' + "tmp = os.path.join(root, 'zz_garbage_test.pdf')",
                d*' ' + 'ok4 = False',
                d*' ' + 'for _c in cands[:3]:',
                d*' ' + '    src = os.path.join(root, _c)',
                d*' ' + "    b0 = os.path.splitext(_c)[0]",
                d*' ' + "    pre = {f for f in os.listdir(root) if f.startswith(b0 + '_') or f.startswith('zz_garbage_test')}",
                d*' ' + '    shutil.copy(src, tmp)',
                d*' ' + '    B.route(tmp, print)',
                d*' ' + '    ok4 = not os.path.exists(tmp)',
                d*' ' + "    post = {f for f in os.listdir(root) if f.startswith(b0 + '_') or f.startswith('zz_garbage_test')}",
                d*' ' + '    for f in post - pre:',
                d*' ' + '        try: os.remove(os.path.join(root, f))',
                d*' ' + '        except Exception: pass',
                d*' ' + '    if os.path.exists(tmp):',
                d*' ' + '        try: os.remove(tmp)',
                d*' ' + '        except Exception: pass',
                d*' ' + '    if ok4: break',
                d*' ' + "ck('S4 wrong-name repair', ok4, '' if ok4 else f'tried: {cands[:3]}')"]
    done.append('S4-cv-witnesses')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done or 'nothing missing')
