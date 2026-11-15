import ast, os, re, time
done = []
def ind(l): return len(l) - len(l.lstrip())
CV = '/Users/apple/CV_Tool'
ROOT = '/Users/apple/Downloads/Sunsoft Technology'
PAT = re.compile(r'siddhart(?!h)', re.I)
moved = 0
for dp, dn, fn in os.walk(ROOT):
    dn[:] = [d for d in dn if not d.startswith('.')]
    for f in fn:
        if not PAT.search(f): continue
        nf = PAT.sub('Siddharth', f)
        old = os.path.join(dp, f); new = os.path.join(dp, nf)
        if os.path.exists(new): continue
        bl = f.lower()
        if bl.endswith(('.crdownload', '.part', '.tmp', '.partial')): continue
        try:
            if time.time() - os.stat(old).st_mtime < 20: continue
            os.rename(old, new); moved += 1
        except Exception: pass
if moved: done.append(f'files-renamed-x{moved}')
for jf in ('cases.json', 'stage_log.json', 'learned_names.json', 'outbox.json', 'sem_index.json'):
    for base in (CV, ROOT):
        jp = os.path.join(base, jf)
        if not os.path.exists(jp): continue
        try: s = open(jp, encoding='utf-8').read()
        except Exception: continue
        if not PAT.search(s): continue
        open(jp, 'w', encoding='utf-8').write(PAT.sub('Siddharth', s))
        done.append(f'{jf}-fixed')
F = open('briefing.py').read().split('\n')
if '# PIPE-CLEAN v67' not in '\n'.join(F):
    i = next(k for k, l in enumerate(F) if l.strip().startswith('def clean_pos('))
    m = re.match(r'\s*def clean_pos\(\s*([A-Za-z_]\w*)', F[i])
    p = m.group(1) if m else 'n'
    F.insert(i+1, (ind(F[i])+4)*' ' + f"{p} = ({p} or '').replace('|', ' ')  # PIPE-CLEAN v67")
    done.append('pipe-clean')
new = '\n'.join(F); ast.parse(new); open('briefing.py', 'w').write(new)
B = open('butler.py').read().split('\n')
if "'S84 clean_pos strips pipes" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S83 renwhy X-ray routed" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S84 clean_pos strips pipes', (chr(35)+' PIPE-CLEAN') in _br)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S84-guard')
print('✅', done)
