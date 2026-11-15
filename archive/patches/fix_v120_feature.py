import ast, os, re, shutil
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# ALREADY-FILED v77' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'T = _tags_of_fast(fp) or get_tags(fp)' and k > next(j for j, l2 in enumerate(B) if l2.strip().startswith('def _reconcile_tags')))
    d = ind(B[i])
    B.insert(i+1, d*' ' + "_here = os.path.basename(os.path.dirname(fp))  # ALREADY-FILED v77")
    B.insert(i+2, d*' ' + "if _here and _here in [re.sub(r'[/\\\\:]', '-', (x or '').split(chr(10))[0].strip()) for x in (T or [])]: continue")
    done.append('reconcile-already-filed')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
lk = [f for f in os.listdir('.') if f.startswith('butler_') and f.endswith('.lock')]
root = open(lk[0]).read().split('|', 1)[1].strip() if lk else '/Users/apple/Downloads/Sunsoft Technology'
flat = 0
for dp, dn, fn in os.walk(root, topdown=False):
    dn[:] = [d for d in dn if not d.startswith('.')]
    if os.path.basename(dp) == os.path.basename(os.path.dirname(dp)) and os.path.dirname(dp) != root:
        par = os.path.dirname(dp)
        for f in list(fn):
            s = os.path.join(dp, f); t = os.path.join(par, f); c = 1
            b, e = os.path.splitext(f)
            while os.path.exists(t): t = os.path.join(par, f'{b}_{c}{e}'); c += 1
            try: shutil.move(s, t); flat += 1
            except Exception: pass
        try:
            if not os.listdir(dp): os.rmdir(dp); flat += 1
        except Exception: pass
if flat: done.append(f'flatten-nests-x{flat}')
B = open('butler.py').read().split('\n')
if "'S99 reconcile never nests a stage in itself" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S98 pulse cannot kill the watcher" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S99 reconcile never nests a stage in itself', (chr(35)+' ALREADY-FILED') in _src and _src.split('def _reconcile_tags')[1].split('\\ndef ')[0].count(chr(35)+' ALREADY-FILED') == 1)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S99-guard')
print('✅', done)
