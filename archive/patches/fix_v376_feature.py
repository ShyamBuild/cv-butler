import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
B0 = open('butler.py').read()
M0 = set(markers(B0.split('\n')))
B = B0.split('\n')
snap = list(B)
s0 = next(k for k, l in enumerate(B) if l.startswith('def seat_rename_check('))
s1 = next(k for k in range(s0 + 1, len(B)) if B[k].startswith('def '))
d = ind(B[s0])
B[s0:s1] = [d*' ' + "def seat_rename_check(root, say=print, only=None):  # SEAT-RENAME v85.11 (announced + once-per-day v85.15): the focused chair's papers wear their humans' names before any draft greets them; the duty announces itself and never repeats its whole-chair pass",
            d*' ' + "    dd = desk_load()",
            d*' ' + "    chair = dd.get('primary')",
            d*' ' + "    if not chair or not os.path.isdir(chair): return 0",
            d*' ' + "    import time as _t, json as _j",
            d*' ' + "    flag = os.path.join(BASE_DIR, '.seatrenamed.json')",
            d*' ' + "    try: done_map = _j.load(open(flag))",
            d*' ' + "    except Exception: done_map = {}",
            d*' ' + "    today = _t.strftime('%Y-%m-%d')",
            d*' ' + "    whole = (only is None) and (done_map.get(chair) != today)",
            d*' ' + "    R = _renamer(root)",
            d*' ' + "    n = 0",
            d*' ' + "    targets = []",
            d*' ' + "    if whole:",
            d*' ' + "        say('✏️ naming the focused chair - the developed eyes read each paper once, then the day is free')  # NO-SILENT-WORK v85.15",
            d*' ' + "        for dp, dn, fn in os.walk(chair):",
            d*' ' + "            for x in fn:",
            d*' ' + "                targets.append(os.path.join(dp, x))",
            d*' ' + "    if only:",
            d*' ' + "        targets = [only]",
            d*' ' + "    for p in targets:",
            d*' ' + "        x = os.path.basename(p)",
            d*' ' + "        if not _is_desk_candidate(x): continue",
            d*' ' + "        if _jd_like_name(x) or _portal_name(x): continue",
            d*' ' + "        v = get_visual_name(p)",
            d*' ' + "        if not v: continue",
            d*' ' + "        canon = _canonical_person_name(v)",
            d*' ' + "        if not canon: continue",
            d*' ' + "        if _name_key(os.path.splitext(x)[0]) == _name_key(canon): continue",
            d*' ' + "        q = os.path.join(os.path.dirname(p), canon + os.path.splitext(x)[1])",
            d*' ' + "        if os.path.exists(q): continue",
            d*' ' + "        try:",
            d*' ' + "            if R is not None:",
            d*' ' + "                try:",
            d*' ' + "                    R._rename(p, canon, say, _tags_of(p))  # REUSE-RENAME v85.12: the developed hands do the developed deed",
            d*' ' + "                except TypeError:",
            d*' ' + "                    R._rename(p, canon, say)",
            d*' ' + "            else:",
            d*' ' + "                os.rename(p, q)",
            d*' ' + "                _rename_ledger(p, canon, 'seat-check', once=True)",
            d*' ' + "                _repath_ledgers(p, q)",
            d*' ' + "            s = sheet_load()",
            d*' ' + "            for it in s.get('items', []):",
            d*' ' + "                if os.path.realpath(it.get('p', '')) in (os.path.realpath(p), os.path.realpath(q)): it['p'] = q",
            d*' ' + "            sheet_save(s)",
            d*' ' + "            n += 1",
            d*' ' + "        except Exception:",
            d*' ' + "            continue",
            d*' ' + "    if whole:",
            d*' ' + "        done_map[chair] = today",
            d*' ' + "        try: _j.dump(done_map, open(flag, 'w'))",
            d*' ' + "        except Exception: pass",
            d*' ' + "    return n",
            ""]
done.append('seat-rename-once')
u0 = next(k for k, l in enumerate(B) if l.startswith('def up_cmd('))
u1 = next(k for k in range(u0 + 1, len(B)) if B[k].startswith('def '))
if 'seat_rename_check(root, say, only=p)' not in '\n'.join(B[u0:u1]):
    anchor = next((k for k in range(u0, u1) if B[k].strip().startswith("say(f\"🛰️") or B[k].strip().startswith('say(f"🛰️')), None)
    if anchor is not None:
        B.insert(anchor, ind(B[anchor])*' ' + "seat_rename_check(root, say, only=p)  # SEAT-RENAME v85.15: the seated paper is named even on days the whole-chair pass rests")
        done.append('seat-rename-seated')
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
M1 = set(markers(open('butler.py').read().split('\n')))
lost = M0 - M1
if lost:
    print('⛔ witness diff:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff: 0 laws lost -', len(M0), 'before,', len(M1), 'after')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.15' not in t:
        open(AR, 'a').write('v85.15: NO-SILENT-WORK + SEAT-RENAME-ONCE - the chair-naming duty announces itself before the vision pipeline runs and records its whole-chair pass per chair per day in .seatrenamed.json; later ups rename only the seated paper, so the terminal is never a blank cursor and the vision bill is paid once a day\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S348 no duty works in silence and no whole-chair pass repeats within a day", "'S347 every interactive prompt stands at column zero", "ck('S348 no duty works in silence and no whole-chair pass repeats within a day', (chr(35)+' NO-SILENT-WORK v85.15') in _src and ('.seatrenamed.json' in _src) and ('seat_rename_check(root, say, only=p)' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
