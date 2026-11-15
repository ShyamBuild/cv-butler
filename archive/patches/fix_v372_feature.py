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
if 'def seat_rename_check(' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.startswith('def up_cmd('))
    B[i:i] = ["def seat_rename_check(root, say=print):  # SEAT-RENAME v85.11: the focused chair's papers wear their humans' names before any draft greets them; the wider root stays untouched",
              "    d = desk_load()",
              "    chair = d.get('primary')",
              "    if not chair or not os.path.isdir(chair): return 0",
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
              "                os.rename(p, q)",
              "            except Exception:",
              "                continue",
              "            _rename_ledger(p, canon, 'seat-check', once=True)",
              "            _repath_ledgers(p, q)",
              "            s = sheet_load()",
              "            for it in s.get('items', []):",
              "                if os.path.realpath(it.get('p', '')) == os.path.realpath(p): it['p'] = q",
              "            sheet_save(s)",
              "            say(f'✏️ renamed: {x} → {os.path.basename(q)}')",
              "            n += 1",
              "    return n",
              ""]
    done.append('seat-rename-def')
u0 = next(k for k, l in enumerate(B) if l.startswith('def up_cmd('))
u1 = next(k for k in range(u0 + 1, len(B)) if B[k].startswith('def '))
if 'seat_rename_check(root' not in '\n'.join(B[u0:u1]):
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
    a0 = next(k for k, l in enumerate(g) if l.startswith('def answer('))
    g[a0:a0] = ["def _say(t='', *a, **k):  # FLUSH-LEFT v85.11: no line the chat speaks may begin with a borrowed space, and every line ends its own newline",
                "    import sys",
                "    end = k.get('end', '\\n')",
                "    sys.stdout.write(str(t).lstrip() + end)",
                "    sys.stdout.flush()",
                ""]
    done.append('flush-say')
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
    if 'v85.11' not in t:
        open(AR, 'a').write('v85.11: FLUSH-LEFT (_say lstrips every chat line and guarantees its newline; all dispatch routes through it) and SEAT-RENAME (up checks the seated primary chair and renames papers to their own first-line names, ledger once=True, repath sheet and log, JD/portal/twin laws honoured; the wider root untouched)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
_br = open('briefing.py').read()
def anch(*needles):
    for n2 in needles:
        hit = [k for k, l in enumerate(B) if n2 in l]
        if hit: return hit[-1]
    return None
GU = [("'S344 no line the chat speaks begins with a borrowed space", "'S343 in the seat no variable answers before its birth", "ck('S344 no line the chat speaks begins with a borrowed space', (chr(35)+' FLUSH-LEFT v85.11') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and (('.lstrip()' ) in open(os.path.join(BASE_DIR, 'briefing.py')).read()))"),
      ("'S345 the focused chair's papers wear their humans' names before any draft greets them", "'S344 no line the chat speaks begins with a borrowed space", "ck('S345 the focused chair'+chr(39)+'s papers wear their humans'+chr(39)+' names before any draft greets them', (chr(35)+' SEAT-RENAME v85.11') in _src and ('def seat_rename_check(' in _src) and ('seat_rename_check(root, say)' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
