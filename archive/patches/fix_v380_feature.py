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
B[s0:s1] = [d*' ' + "def seat_rename_check(root, say=print, only=None):  # SEAT-RENAME v85.11 (announced-first + lazy + budgeted v85.17): the focused chair's papers wear their humans' names before any draft greets them",
            d*' ' + "    import time as _t, json as _j",
            d*' ' + "    dd = desk_load()",
            d*' ' + "    chair = dd.get('primary')",
            d*' ' + "    if not chair or not os.path.isdir(chair): return 0",
            d*' ' + "    flag = os.path.join(BASE_DIR, '.seatrenamed.json')",
            d*' ' + "    try: done_map = _j.load(open(flag))",
            d*' ' + "    except Exception: done_map = {}",
            d*' ' + "    today = _t.strftime('%Y-%m-%d')",
            d*' ' + "    whole = (only is None) and (done_map.get(chair) != today)",
            d*' ' + "    targets = []",
            d*' ' + "    if whole:",
            d*' ' + "        for dp, dn, fn in os.walk(chair):",
            d*' ' + "            for x in fn:",
            d*' ' + "                if _is_desk_candidate(x): targets.append(os.path.join(dp, x))",
            d*' ' + "        say(f'✏️ naming the focused chair ({len(targets)} papers) - text eyes first, pixels only if silent, ninety seconds per up')  # NO-SILENT-WORK v85.15: the announcement precedes every cost, constructors included",
            d*' ' + "    if only:",
            d*' ' + "        targets = [only]",
            d*' ' + "    R = None",
            d*' ' + "    n = 0",
            d*' ' + "    t0 = _t.time()",
            d*' ' + "    completed = True",
            d*' ' + "    for p in targets:",
            d*' ' + "        if whole and (_t.time() - t0) > 90:  # CEREMONY-BUDGET v85.17: ninety seconds of eyes per up; the rest resumes at the next keystroke, and the day-flag waits for a finished walk",
            d*' ' + "            completed = False",
            d*' ' + "            say('⏳ naming pauses here - the next up resumes the chair')",
            d*' ' + "            break",
            d*' ' + "        x = os.path.basename(p)",
            d*' ' + "        if not _is_desk_candidate(x): continue",
            d*' ' + "        if _jd_like_name(x) or _portal_name(x): continue",
            d*' ' + "        v = heuristic_name(p) or get_visual_name(p)  # TEXT-EYES v85.16: the text eyes are asked before the vision eyes; vision remains the fallback, not the first resort",
            d*' ' + "        if not v: continue",
            d*' ' + "        canon = _canonical_person_name(v)",
            d*' ' + "        if not canon: continue",
            d*' ' + "        if _name_key(os.path.splitext(x)[0]) == _name_key(canon): continue",
            d*' ' + "        q = os.path.join(os.path.dirname(p), canon + os.path.splitext(x)[1])",
            d*' ' + "        if os.path.exists(q): continue",
            d*' ' + "        if canon and _name_key(canon) != _name_key(os.path.splitext(x)[0]): say(f'👁️ {x} → eyes {v!r} → canon {canon!r}')  # NAME-EVIDENCE v85.16: when the eyes and the filename disagree, the receipt names every gate between them",
            d*' ' + "        try:",
            d*' ' + "            if R is None: R = _renamer(root)  # LAZY-RENAMER v85.17: the developed hands are woken only when a rename is actually owed",
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
            d*' ' + "    if whole and completed:",
            d*' ' + "        done_map[chair] = today",
            d*' ' + "        try: _j.dump(done_map, open(flag, 'w'))",
            d*' ' + "        except Exception: pass",
            d*' ' + "    return n",
            ""]
done.append('ceremony-reordered')
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
    if 'v85.17' not in t:
        open(AR, 'a').write('v85.17: the announcement precedes every cost including constructors; the renamer wakes lazily at the first owed rename; the ceremony carries a ninety-second budget per up with resume-next-up and a day-flag that waits for a finished walk (S351)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S351 the announcement precedes every cost, and no constructor runs before its duty speaks", "'S350 when the eyes and the filename disagree, the receipt names every gate between them", "ck('S351 the announcement precedes every cost, and no constructor runs before its duty speaks', (lambda seg: seg.find('naming the focused chair') < seg.find('_renamer(root)') and seg.find('naming the focused chair') >= 0)(_src.split('def seat_rename_check(')[1].split(chr(10) + 'def ')[0]))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
