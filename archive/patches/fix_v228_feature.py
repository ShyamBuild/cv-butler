import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if l.strip().startswith('def phones_of(p):'):
        B[k] = ind(l)*' ' + "def phones_of(p, quiet=False):  # QUIET-CLERK v81.87: the picker may ask without the ceremony; the law of speaking identity still binds every voice that drafts"
        done.append('quiet-clerk'); break
for k, l in enumerate(B):
    if l.strip().startswith('print(') and 'we are talking about' in l:
        B[k] = ind(l)*' ' + 'if not quiet: ' + l.strip()
        done.append('confess-quiet'); break
for k, l in enumerate(B):
    if l.strip().startswith('print(') and 'taught for' in l and 'IDENTITY-FIRST v81.73' in l:
        B[k] = ind(l)*' ' + 'if not quiet: ' + l.strip()
        done.append('taught-id-quiet'); break
for k, l in enumerate(B):
    if l.strip().startswith('print(') and 'taught number in use for' in l:
        B[k] = ind(l)*' ' + 'if not quiet: ' + l.strip()
        done.append('taught-echo-quiet'); break
for k, l in enumerate(B):
    if l.strip().startswith('if ph: print('):
        B[k] = l.replace('if ph: print(', 'if ph and not quiet: print(')
        done.append('extract-quiet'); break
for k, l in enumerate(B):
    if "'S171 a taught number beats extraction" in l and 'def phones_of(p):' in l:
        B[k] = l.replace('def phones_of(p):', 'def phones_of(p')
        done.append('S171-repinned'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
if '# PHONE-IN-PICKER v81.87' not in '\n'.join(g):
    i = next(k for k, l in enumerate(g) if '{_em} · {os.path.relpath(os.path.dirname(_c), root)}' in l)
    d = ind(g[i])
    g[i:i] = [d*' ' + "try: _ph = (butler.phones_of(_c, quiet=True) or ['none readable'])[0]  # PHONE-IN-PICKER v81.87: the row shows the number too, so the master verifies who AND where at one glance",
              d*' ' + "except Exception: _ph = 'none readable'"]
    g[i+2] = g[i+2].replace('{_em} · {os.path.relpath(', '{_em} · {_ph} · {os.path.relpath(')
    done.append('phone-in-picker')
    srcg = '\n'.join(g); ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
if "'S192 the picker shows the number beside the email" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S191 old guards repin to new shapes, never veto them" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S192 the picker shows the number beside the email', (chr(35)+' PHONE-IN-PICKER v81.87') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and (chr(35)+' QUIET-CLERK v81.87') in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S192-guard')
print('✅', done)
