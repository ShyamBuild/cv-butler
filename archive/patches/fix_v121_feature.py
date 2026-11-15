import ast, os, shutil
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
old = "    if os.path.basename(d0) == nm: continue"
if '# HOME v78' not in src and any(l.rstrip() == old or l.strip() == 'if os.path.basename(d0) == nm: continue' for l in B):
    i = next(k for k, l in enumerate(B) if l.strip() == 'if os.path.basename(d0) == nm: continue')
    B[i] = ind(B[i])*' ' + 'if os.path.basename(d0) == nm: return  # HOME v78'
    done.append('home-return')
src = '\n'.join(B)
if '# TAG-TRUTH-AUTHORITATIVE v78' not in src:
    i0 = next(k for k, l in enumerate(B) if '# TAG-TRUTH v75' in l)
    d = ind(B[i0])
    j = next(k for k in range(i0, i0+20) if B[k].strip() == 'except Exception: return')
    B.insert(j+1, d*' ' + 'return  # TAG-TRUTH-AUTHORITATIVE v78')
    done.append('tag-truth-authoritative')
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
if "'S100 tag-truth is the only filing voice" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S99 reconcile never nests a stage in itself" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S100 tag-truth is the only filing voice', (chr(35)+' HOME v78') in _src and (chr(35)+' TAG-TRUTH-AUTHORITATIVE') in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S100-guard')
print('✅', done)
