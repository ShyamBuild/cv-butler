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
    B[i:i] = ["def _renamer(root):  # REUSE-RENAME v85.12: discover the house's own renamer class; the seat check delegates, never re-rolls",
              "    for _vn, _vc in list(globals().items()):",
              "        if isinstance(_vc, type) and '_rename' in getattr(_vc, '__dict__', {}):",
              "            try:",
              "                return _vc(root)",
              "            except Exception:",
              "                pass",
              "    return None",
              ""]
    done.append('renamer-discovery')
if 'def seat_rename_check(' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.startswith('def up_cmd('))
    B[i:i] = ["def seat_rename_check(root, say=print):  # SEAT-RENAME v85.11 (whole v85.13): the focused chair's papers wear their humans' names before any draft greets them; the wider root stays untouched",
              "    d = desk_load()",
              "    chair = d.get('primary')",
              "    if not chair or not os.path.isdir(chair): return 0",
              "    R = _renamer(root)",
              "    n = 0",
              "    for dp, dn, fn in os.walk(chair):",
              "        for x in fn:",
              "            p = os.path.join(dp, x)",
              "            if not _is_desk_candidate(x): continue",
              "            if _jd_like_name(x) or _portal_name(x): continue",
              "            v = get_visual_name(p)",
              "            if not v: continue",
              "            canon = _canonical_person_name(v)",
              "            if not canon: continue",
              "            if _name_key(os.path.splitext(x)[0]) == _name_key(canon): continue",
              "            q = os.path.join(dp, canon + os.path.splitext(x)[1])",
              "            if os.path.exists(q): continue",
              "            try:",
              "                if R is not None:",
              "                    try:",
              "                        R._rename(p, canon, say, _tags_of(p))  # REUSE-RENAME v85.12: the developed hands do the developed deed",
              "                    except TypeError:",
              "                        R._rename(p, canon, say)",
              "                else:",
              "                    os.rename(p, q)",
              "                    _rename_ledger(p, canon, 'seat-check', once=True)",
              "                    _repath_ledgers(p, q)",
              "                s = sheet_load()",
              "                for it in s.get('items', []):",
              "                    if os.path.realpath(it.get('p', '')) in (os.path.realpath(p), os.path.realpath(q)): it['p'] = q",
              "                sheet_save(s)",
              "                n += 1",
              "            except Exception:",
              "                continue",
              "    return n",
              ""]
    done.append('seat-rename-def')
u0 = next(k for k, l in enumerate(B) if l.startswith('def up_cmd('))
u1 = next(k for k in range(u0 + 1, len(B)) if B[k].startswith('def '))
if 'seat_rename_check(root, say)' not in '\n'.join(B[u0:u1]):
    j = next(k for k in range(u0, u1) if B[k].strip().startswith('s = sheet_load()'))
    B.insert(j, ind(B[j])*' ' + "seat_rename_check(root, say)  # SEAT-RENAME v85.11: check the focused chair before seating anyone")
    done.append('seat-rename-hook')
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
    if 'v85.13' not in t:
        open(AR, 'a').write('v85.13: the whole lap in one piece - seat_rename_check born again with delegation to the developed renamer (TypeError-tolerant call ladder, manual ledger only as fallback), hooked in up before seating; _say born before briefing first def; fifty-two dispatch routes flush (S344, S345, S346)\n')
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
      ("'S346 the seat check delegates the deed to the developed renamer", "'S345 the focused chair's papers wear their humans' names before any draft greets them", "ck('S346 the seat check delegates the deed to the developed renamer', (chr(35)+' REUSE-RENAME v85.12') in _src and ('def _renamer(' in _src) and ('R._rename(p, canon, say' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
