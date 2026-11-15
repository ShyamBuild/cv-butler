import ast
done = []
p = 'butler.py'; L = open(p).read().split('\n')
i = next(k for k, l in enumerate(L) if 'zz_garbage_test.pdf' in l and 'tmp =' in l)
a = i
j = next(k for k in range(i, len(L)) if 'os.remove(os.path.join(root, f))' in L[k])
d = len(L[a]) - len(L[a].lstrip())
L[a:j+1] = [d*' ' + "SKIPD = ('converted files', 'converted doc files', 'duplicates', 'previous versions')",
            d*' ' + 'wit = None',
            d*' ' + 'for dp, dn, fn in os.walk(root):',
            d*' ' + "    dn[:] = [x for x in dn if not x.startswith('.') and x.lower() not in SKIPD]",
            d*' ' + '    for f in sorted(fn):',
            d*' ' + '        fl = f.lower()',
            d*' ' + "        if fl.endswith('.pdf') and not f.startswith('zz_') and not fl.startswith('jd') and ' jd' not in fl and '_jd' not in fl and not fl.startswith('regional') and 'location' not in fl:",
            d*' ' + '            wit = os.path.join(dp, f); break',
            d*' ' + '    if wit: break',
            d*' ' + "tmp = os.path.join(root, 'zz_garbage_test.pdf')",
            d*' ' + 'ok4 = False',
            d*' ' + 'if wit:',
            d*' ' + "    b0 = os.path.splitext(os.path.basename(wit))[0]; e = '.pdf'",
            d*' ' + '    pre = set(os.listdir(root))',
            d*' ' + '    shutil.copy(wit, tmp)',
            d*' ' + '    B.route(tmp, print)',
            d*' ' + '    ok4 = not os.path.exists(tmp)',
            d*' ' + '    for f in set(os.listdir(root)) - pre:',
            d*' ' + "        if f.startswith('zz_') or f == b0 + e or re.match(re.escape(b0) + r'_\\d+' + e + '$', f):",
            d*' ' + '            try: os.remove(os.path.join(root, f))',
            d*' ' + '            except Exception: pass',
            d*' ' + '    if os.path.exists(tmp):',
            d*' ' + '        try: os.remove(tmp)',
            d*' ' + '        except Exception: pass',
            d*' ' + "ck('S4 wrong-name repair', ok4, '' if ok4 else f'witness: {wit}')"]
done.append('S4-recursive-witness')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
s = open('ship.sh').read().split('\n')
for k, l in enumerate(s):
    if l.startswith('ROOT="$(cat ~/.cvtool_last_butler_root'):
        s[k] = 'PRIMARY="/Users/apple/Downloads/Sunsoft Technology/04 Avis/Regional Head - Sales || Vikhroli East- Mumbai  Location"\nROOT="${CV_ROOT:-$PRIMARY}"'
        if k+1 < len(s) and s[k+1].startswith('[ -z "$ROOT" ] && ROOT='):
            del s[k+1]
        done.append('ship-root-pinned')
        break
open('ship.sh', 'w').write('\n'.join(s))
print('✅', done or 'nothing missing')
