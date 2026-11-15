import ast, re, subprocess
p = 'butler.py'; L = open(p).read().split('\n'); done = []
# 1) rule-based: any self. outside class Butler is module-scope bug -> B.
in_cls = False; fixed = 0
for i, l in enumerate(L):
    if l.startswith('class '):
        in_cls = True; continue
    if in_cls and l.strip() and not l[0].isspace():
        in_cls = False
    if (not in_cls) and re.search(r'(?<![A-Za-z0-9_])self\.', l):
        L[i] = re.sub(r'(?<![A-Za-z0-9_])self\.', 'B.', l); fixed += 1
if fixed: done.append(f'module-scope self->B x{fixed}')
# 2) startup reconcile+compact right after the initial scan settles
a = None
for i, l in enumerate(L):
    if 'Scan complete' in l and ('say(' in l or 'print(' in l):
        a = i
if a is not None and not any('startup-reconcile' in x for x in L[a+1:a+5]):
    d = len(L[a]) - len(L[a].lstrip())
    L[a+1:a+1] = [d*' ' + 'try:',
                  d*' ' + '    B._reconcile_tags(print)',
                  d*' ' + '    B._compact_numbers(B.root, print)',
                  d*' ' + 'except Exception as _se:',
                  d*' ' + "    print('startup-reconcile error:', _se)"]
    done.append('startup-reconcile')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done or 'nothing missing')
r = subprocess.run(['cv_env/bin/python3', '-c', '''
import butler, os
print("engines:", butler.detect_engines())
for c in ("/Applications/Pages.app", "/System/Applications/Pages.app"):
    print("probe", c, os.path.isdir(c))
src = open("butler.py").read()
left = [l for l in src.split(chr(10)) if "self." in l and l[:1] not in (" ", chr(9))]
print("indent-0 self. lines left:", len(left))
'''], capture_output=True, text=True, cwd='.')
print(r.stdout.strip() or r.stderr.strip()[-400:])
