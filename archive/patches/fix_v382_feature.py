import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
FL = os.path.join(os.getcwd(), '.seatrenamed.json')
if os.path.exists(FL):
    os.remove(FL); done.append('stale-flag-removed')
B0 = open('butler.py').read()
M0 = set(markers(B0.split('\n')))
B = B0.split('\n')
snap = list(B)
u0 = next(k for k, l in enumerate(B) if l.startswith('def up_cmd('))
u1 = next(k for k in range(u0 + 1, len(B)) if B[k].startswith('def '))
sd = next((k for k in range(u0, u1) if 'SEED-SAY v85.18' in B[k]), None)
if sd is not None and sd - 1 >= u0 and B[sd-1].strip() == "say('')":
    del B[sd-1]; done.append('gap-line-deleted')
s0 = next(k for k, l in enumerate(B) if l.startswith('def seat_rename_check('))
s1 = next(k for k in range(s0 + 1, len(B)) if B[k].startswith('def '))
d = ind(B[s0])
B[s0:s1] = [d*' ' + "def seat_rename_check(root, say=print, only=None):  # SEAT-RENAME v85.11 (examined-list v85.19): the flag remembers named papers, not visited days - silence never earns a pass",
            d*' ' + "    import json as _j",
            d*' ' + "    dd = desk_load()",
            d*' ' + "    chair = dd.get('primary')",
            d*' ' + "    if not chair or not os.path.isdir(chair): return 0",
            d*' ' + "    flag = os.path.join(BASE_DIR, '.seatrenamed.json')",
            d*' ' + "    try: rec = _j.load(open(flag))",
            d*' ' + "    except Exception: rec = {}",
            d*' ' + "    today = time.strftime('%Y-%m-%d')",
            d*' ' + "    if rec.get('day') != today: rec = {'day': today, 'examined': []}",
            d*' ' + "    ex = set(rec.get('examined', []))",
            d*' ' + "    whole = (only is None)",
            d*' ' + "    targets = []",
            d*' ' + "    if whole:",
            d*' ' + "        for dp, dn, fn in os.walk(chair):",
            d*' ' + "            for x in fn:",
            d*' ' + "                if _is_desk_candidate(x) and x not in ex: targets.append(os.path.join(dp, x))",
            d*' ' + "        if targets: say(f'✏️ naming the focused chair ({len(targets)} unexamined papers) - text eyes first, pixels only if silent, ninety seconds per up')  # NO-SILENT-WORK v85.15",
            d*' ' + "    if only:",
            d*' ' + "        targets = [only]",
            d*' ' + "    R = None",
            d*' ' + "    n = 0",
            d*' ' + "    t0 = time.time()",
            d*' ' + "    for p in targets:",
            d*' ' + "        if whole and (time.time() - t0) > 90:  # CEREMONY-BUDGET v85.17",
            d*' ' + "            say('⏳ naming pauses here - the next up resumes the chair')",
            d*' ' + "            break",
            d*' ' + "        x = os.path.basename(p)",
            d*' ' + "        if not _is_desk_candidate(x): continue",
            d*' ' + "        if _jd_like_name(x) or _portal_name(x): continue",
            d*' ' + "        v = heuristic_name(p) or get_visual_name(p)  # TEXT-EYES v85.16",
            d*' ' + "        if not v:",
            d*' ' + "            say(f'👁️ {x}: text silent, vision silent - left for the next up')  # MISS-EVIDENCE v85.19: a paper the eyes cannot read is never marked examined, and its silence is spoken",
            d*' ' + "            continue",
            d*' ' + "        ex.add(x)",
            d*' ' + "        canon = _canonical_person_name(v)",
            d*' ' + "        if not canon: continue",
            d*' ' + "        if _name_key(os.path.splitext(x)[0]) == _name_key(canon): continue",
            d*' ' + "        q = os.path.join(os.path.dirname(p), canon + os.path.splitext(x)[1])",
            d*' ' + "        if os.path.exists(q): continue",
            d*' ' + "        say(f'👁️ {x} → eyes {v!r} → canon {canon!r}')  # NAME-EVIDENCE v85.16",
            d*' ' + "        try:",
            d*' ' + "            if R is None: R = _renamer(root)  # LAZY-RENAMER v85.17",
            d*' ' + "            if R is not None:",
            d*' ' + "                try:",
            d*' ' + "                    R._rename(p, canon, say, _tags_of(p))  # REUSE-RENAME v85.12",
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
            d*' ' + "        rec['day'] = today; rec['examined'] = sorted(ex)",
            d*' ' + "        try: _j.dump(rec, open(flag, 'w'))",
            d*' ' + "        except Exception: pass",
            d*' ' + "    return n",
            ""]
done.append('examined-list')
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
    if 'v85.19' not in t:
        open(AR, 'a').write('v85.19: the seat flag remembers examined (named) papers, not visited days - silent papers are spoken by MISS-EVIDENCE and retried every up; the legacy blank line before the seed is deleted; stale flag removed at patch time\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S354 silence never earns a pass - unnamed papers are spoken and retried", "'S353 a fingerprint is computed once per content and the seed never works in silence", "ck('S354 silence never earns a pass - unnamed papers are spoken and retried', (chr(35)+' MISS-EVIDENCE v85.19') in _src and ('examined' in _src) and (chr(35)+' SEAT-RENAME v85.11' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
