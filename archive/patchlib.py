import ast, os, re
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines: out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
def perfile(root='.'):
    S = {}
    for fn in ('butler.py', 'briefing.py', 'wa.py'):
        P = os.path.join(root, fn)
        S[fn] = set(markers(open(P).read().split('\n'))) if os.path.exists(P) else set()
    return S
def read(fn='butler.py'): return open(fn).read().split('\n')
def write(B, fn='butler.py'):
    src = '\n'.join(B)
    if fn.endswith('.py'): ast.parse(src)
    open(fn, 'w').write(src); return src
def write_raw(B, fn):  # PATCHLIB v85.94: shells and texts write without a python parser judging them
    open(fn, 'w').write('\n'.join(B)); return True
def preflight(B, M0, fn='butler.py'):  # PATCHLIB v85.94: parse, witness and marker-carry checked BEFORE any write, so a bad lap dies childless
    src = '\n'.join(B)
    if fn.endswith('.py'): ast.parse(src)
    cur = set(markers(src.split('\n')))
    return M0.get(fn, set()) - cur
def sub_in_line(B, old, new, marker):
    n = 0
    for k, l in enumerate(B):
        if old in l and marker not in l:
            head, tail = l.split(old, 1)
            B[k] = head + new + tail.rstrip() + '  # ' + marker
            n += 1
    return n
def insert_before(B, anchor, block, once_marker=None):
    k = next((i for i, l in enumerate(B) if anchor in l), None)
    if k is None: return 0
    if once_marker and once_marker in '\n'.join(B[max(0,k-30):k+30]): return 0
    d = ind(B[k])
    print('🔎 neighbourhood of anchor %r:' % anchor[:40])
    for j in range(max(0,k-2), min(k+3, len(B))): print('   |', B[j].rstrip()[:140])
    B[k:k] = [(d + e)*' ' + s for e, s in block]
    return 1
def insert_after(B, anchor, block, once_marker=None):
    k = next((i for i, l in enumerate(B) if anchor in l), None)
    if k is None: return 0
    if once_marker and once_marker in '\n'.join(B[k:k+30]): return 0
    d = ind(B[k])
    B[k+1:k+1] = [(d + e)*' ' + s for e, s in block]
    return 1
def replace_function(B, name, new_body):
    k = next((i for i, l in enumerate(B) if l.startswith('def %s(' % name)), None)
    if k is None: return 0
    k1 = next((i for i in range(k+1, len(B)) if B[i].startswith('def ') or (B[i].strip() and not B[i].startswith(' ') and not B[i].startswith('#'))), len(B))
    print('🔎 replacing %s lines %d-%d, old body carried markers: %s' % (name, k+1, k1, sorted(set(markers(B[k:k1])))))
    d = ind(B[k])
    B[k:k1] = [(d + e)*' ' + s for e, s in new_body]
    return 1
def append_module(B, block):
    while B and B[-1].strip() == '': B.pop()
    B += [''] + [(e)*' ' + s for e, s in block]
    return 1
def witness(M0, root='.'):
    M1 = perfile(root); lost = set()
    for fn in M0: lost |= (M0[fn] - M1.get(fn, set()))
    if lost:
        print('⛔ witness diff per file:', sorted(lost)); raise SystemExit('harvest first')
    print('🔎 witness diff per file: 0 laws lost')
    return M1
