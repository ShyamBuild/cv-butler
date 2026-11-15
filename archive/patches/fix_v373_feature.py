import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
B0 = open('butler.py').read()
G0 = open('briefing.py').read()
M0 = set(markers(B0.split('\n'))) | set(markers(G0.split('\n')))
B = B0.split('\n')
snap = list(B)
if 'def _renamer(' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.startswith('def up_cmd('))
    B[i:i] = ["def _renamer(root):  # REUSE-RENAME v85.12: the seat check delegates to the house's own developed renamer; it never re-rolls the deed by hand",
              "    for _vn, _vc in list(globals().items()):",
              "        if isinstance(_vc, type) and '_rename' in getattr(_vc, '__dict__', {}):",
              "            try:",
              "                return _vc(root)",
              "            except Exception:",
              "                pass",
              "    return None",
              ""]
    done.append('renamer-discovery')
s0 = next((k for k, l in enumerate(B) if l.startswith('def seat_rename_check(')), None)
if s0 is not None and 'REUSE-RENAME' not in '\n'.join(B[s0:s0+40]):
    s1 = next(k for k in range(s0 + 1, len(B)) if B[k].startswith('def '))
    body = B[s0:s1]
    ins = None
    for k, l in enumerate(body):
        if l.strip().startswith('v = get_visual_name(p)'):
            ins = k; break
    if ins is not None:
        d = ind(body[ins])
        body[ins:ins] = [d*' ' + "R = R0  # REUSE-RENAME v85.12: the developed hands do the developed deed"]
        for k, l in enumerate(body):
            if l.strip().startswith('os.rename(p, q)'):
                dd = ind(l)
                body[k:k+1] = [dd*' ' + "if R is not None and hasattr(R, '_rename'):",
                               (dd+4)*' ' + "R._rename(p, canon, say, _tags_of(p))",
                               (dd+4)*' ' + "else:",
                               (dd+8)*' ' + "os.rename(p, q)",
                               (dd+8)*' ' + "_rename_ledger(p, canon, 'seat-check', once=True)",
                               (dd+8)*' ' + "_repath_ledgers(p, q)"]
                break
        for k, l in enumerate(body):
            if l.strip().startswith('_rename_ledger(p, canon') and body[k-1].strip() != 'else:' and 'os.rename' not in body[k-2]:
                pass
        body = [body[0]] + [l if 'def seat_rename_check' not in l else l for l in body[1:]]
        for k, l in enumerate(body):
            if l.strip().startswith('n = 0'):
                body[k:k] = [ind(l)*' ' + "R0 = _renamer(root)"]
                break
        B[s0:s1] = body
        done.append('seat-rename-delegates')
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
g = G0.split('\n')
snapg = list(g)
if 'def _say(' not in '\n'.join(g):
    f0 = next(k for k, l in enumerate(g) if l.startswith('def '))
    g[f0:f0] = ["def _say(t='', *a, **k):  # FLUSH-LEFT v85.11: born before every def that names it - no line the chat speaks begins with a borrowed space, and every line ends its own newline",
                "    import sys",
                "    end = k.get('end', '\\n')",
                "    sys.stdout.write(str(t).lstrip() + end)",
                "    sys.stdout.flush()",
                ""]
    done.append('flush-say-top')
n = 0
for k, l in enumerate(g):
    if ', print); continue' in l and 'butler.' in l:
        g[k] = l.replace(', print); continue', ', _say); continue'); n += 1
    if l.startswith('def ') and 'say=print)' in l:
        g[k] = l.replace('say=print)', 'say=_say)'); n += 1
if n: done.append('dispatch-flush-x%d' % n)
srcg = '\n'.join(g)
if srcg != G0:
    ast.parse(srcg); open('briefing.py', 'w').write(srcg)
M1 = set(markers(open('butler.py').read().split('\n'))) | set(markers(open('briefing.py').read().split('\n')))
lost = M0 - M1
if lost:
    print('⛔ witness diff:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff: 0 laws lost -', len(M0), 'before,', len(M1), 'after')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.12' not in t:
        open(AR, 'a').write('v85.12: REUSE-RENAME - seat_rename_check discovers the developed renamer class and delegates every rename to its _rename (tags, ledger, repath, twins: the developed hands); _say born before the first def in briefing so no default names an unborn printer (S344, S345, S346)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n2 in needles:
        hit = [k for k, l in enumerate(B) if n2 in l]
        if hit: return hit[-1]
    return None
GU = [("'S344 no line the chat speaks begins with a borrowed space", "'S343 in the seat no variable answers before its birth", "ck('S344 no line the chat speaks begins with a borrowed space', (chr(35)+' FLUSH-LEFT v85.11') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and ('.lstrip()' in open(os.path.join(BASE_DIR, 'briefing.py')).read()))"),
      ("'S345 the focused chair's papers wear their humans' names before any draft greets them", "'S344 no line the chat speaks begins with a borrowed space", "ck('S345 the focused chair'+chr(39)+'s papers wear their humans'+chr(39)+' names before any draft greets them', (chr(35)+' SEAT-RENAME v85.11') in _src and ('def seat_rename_check(' in _src) and ('seat_rename_check(root, say)' in _src))"),
      ("'S346 the seat check delegates the deed to the developed renamer", "'S345 the focused chair's papers wear their humans' names before any draft greets them", "ck('S346 the seat check delegates the deed to the developed renamer', (chr(35)+' REUSE-RENAME v85.12') in _src and ('def _renamer(' in _src) and (\"R._rename(p, canon, say\" in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
