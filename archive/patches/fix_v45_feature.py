import ast
p = 'briefing.py'; L = open(p).read().split('\n'); done = []
def ind(l): return len(l) - len(l.lstrip())
if 'def _phones_by_basename(' not in '\n'.join(L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def _phone_first('))
    d = ind(L[i])
    L[i:i] = [d*' ' + 'def _phones_by_basename(p):',
              d*' ' + '    try:',
              d*' ' + '        dd = json.load(open(PHONES_FILE)) if os.path.exists(PHONES_FILE) else {}',
              d*' ' + '    except Exception:',
              d*' ' + '        return []',
              d*' ' + '    b = os.path.basename(p).lower()',
              d*' ' + '    for k, v in dd.items():',
              d*' ' + '        if os.path.basename(k).lower() == b: return v.get(\'phones\') or []',
              d*' ' + '    return []',
              '']
    done.append('phones-basename-alias')
L = open(p).read().split('\n') if False else L
n = 0
for k, l in enumerate(L):
    if '_pick_phone(phones_of(hit), say)' in l:
        L[k] = l.replace('_pick_phone(phones_of(hit), say)', '_pick_phone(phones_of(hit) or _phones_by_basename(hit), say)'); n += 1
if n: done.append(f'pick-phone-alias-x{n}')
for k, l in enumerate(L):
    if "cmd == 'nudge'" in l and 'do_missed(' not in l:
        L[k] = l.split(':')[0] + ': do_missed(arg, root, print)'; done.append('cli-nudge-to-missed'); break
for k, l in enumerate(L):
    if "startswith('nudge')" in l and 'do_missed(' not in l:
        L[k] = ind(l)*' ' + l.strip().split(':', 1)[0] + ': do_missed(q[len("nudge"):].strip(), root); continue'
        done.append('chat-nudge-to-missed'); break
for k, l in enumerate(L):
    if l.strip().startswith("for dp, dn, fn in ([] if hit else os.walk(f['path'])):"):
        d = ind(l); region = L[k+1:k+5]
        L[k:k+5] = [d*' ' + "for _sr in ([] if hit else [f['path'], os.path.dirname(os.path.dirname(f['path']))]):",
                    (d+4)*' ' + 'for dp, dn, fn in os.walk(_sr):'] + \
                   [((ind(x)+4) if x.strip() else 0)*' ' + x.strip() for x in region] + \
                   [(d+4)*' ' + 'if hit: break']
        done.append('walk-escalates-to-client'); break
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
B = open('butler.py').read().split('\n')
if "'S27 nudge routes" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S26 scan index per-root only" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S27 nudge routes to tree-walk resolver + phones follow moves', 'def _phones_by_basename(' in _br and \"for _sr in ([] if hit else [f['path']\" in _br)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S27-guard')
print('✅', done or 'nothing missing')
