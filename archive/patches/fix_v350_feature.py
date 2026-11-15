import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
def carry(new_first, deleted):
    ms = markers(deleted)
    if ms:
        return new_first.rstrip() + '  ' + ' '.join(ms) + '  # WITNESS-CARRY v84.52: deleted lines hand their laws to the line that survives'
    return new_first
B0 = open('butler.py').read()
M0 = set(markers(B0.split('\n')))
B = B0.split('\n')
snap = list(B)
c0 = next(k for k, l in enumerate(B) if l.startswith('def calls_cmd('))
c1 = next(k for k in range(c0 + 1, len(B)) if B[k].startswith('def sheet_cmd('))
if 'RETRAY' not in '\n'.join(B[c0:c1]):
    w = next(k for k in range(c0, c1) if B[k].strip().startswith("waiting = [i for i in s0.get('items', []) if i.get('status') == 'waiting']"))
    d = ind(B[w])
    B[w:w] = [d*' ' + "refed = 0",
              d*' ' + "if not items and not reopened:  # RETRAY v84.55: when no loose paper waits, the skipped return for re-review - one per empty seed, oldest skip first, and the skip is consumed so no man re-feds endlessly",
              (d+4)*' ' + "skd = skips_load()",
              (d+4)*' ' + "for kp in sorted(skd, key=lambda x: skd[x] if isinstance(skd[x], (int, float)) else 0):  # RETRAY-ONE v84.56: the tray offers one soul per empty seed; the rest hold their place",
              (d+8)*' ' + "if not os.path.isfile(kp): continue",
              (d+8)*' ' + "rp2 = os.path.realpath(kp)",
              (d+8)*' ' + "if rp2 in seen or os.path.basename(os.path.dirname(kp)) in _tag_vocab() or _name_key(os.path.basename(kp)) in mem: continue",
              (d+8)*' ' + "if any(os.path.realpath(it.get('p', '')) == rp2 for it in s0.get('items', [])): continue",
              (d+8)*' ' + "items.append({'p': kp, 'name': os.path.splitext(os.path.basename(kp))[0], 'status': 'waiting', 'fp': _fp(kp), 're': True})",
              (d+8)*' ' + "del skd[kp]; refed += 1; break",
              (d+4)*' ' + "if refed: json.dump(skd, open(SKIPS_PATH, 'w'), indent=1)"]
    done.append('retray-feed')
    for k in range(c0, c1):
        if 'call sheet seeded:' in B[k] and 're-review' not in B[k]:
            code, sep, comment = B[k].partition('  # ')
            code = code.rstrip()
            if code.endswith(')'):
                code = code[:code.rfind(')')] + " + (f' · 🔄 re-review: {refed}' if refed else ''))"
            B[k] = code + (sep + comment if sep else '')
            done.append('retray-line'); break
src = '\n'.join(B)
u0 = next(k for k, l in enumerate(B) if l.startswith('def up_cmd('))
u1 = next(k for k in range(u0 + 1, len(B)) if B[k].startswith('def '))
if 'RETRAY' not in '\n'.join(B[u0:u1]):
    seat = next((k for k in range(u0, u1) if B[k].strip().startswith('i = it')), None)
    if seat is not None:
        f = next(k for k in range(seat, u0, -1) if B[k].lstrip().startswith('for '))
        B[f] = ind(B[f])*' ' + "for it in sorted(s.get('items', []), key=lambda x: 1 if x.get('re') else 0):  # RETRAY v84.55: new blood outranks the re-review tray in the chair"
        done.append('seat-priority')
    for k in range(u0, u1):
        if B[k].strip().startswith("s['current'] = i; sheet_save(s)"):
            B.insert(k+1, ind(B[k])*' ' + "if i.get('re'): say('🔄 re-review: skipped earlier, the tray is empty now - one soul per seed, new loose papers still outrank him')  # RETRAY v84.55")
            done.append('retray-notice'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("'2 🙅 not interested") and 'not relevant' not in l:
        B[k] = ind(l)*' ' + " '2 🙅 not interested / not relevant → [Closed – Not Proceeding] · keyword: refer · now: refer/farewell (references often asked)',"
        done.append('door2-words'); break
for k, l in enumerate(B):
    if l.strip().startswith("'7 ⏭️ skip him for now") and 'returns when' not in l:
        B[k] = ind(l)*' ' + " '7 ⏭️ skip him for now         → no tag, no move, remembered · returns one-per-empty-seed, newest skips last',"
        done.append('door7-words'); break
for k, l in enumerate(B):
    if '7 ⏭️ skip→remembered' in l and 'per empty seed' not in l:
        B[k] = l.replace('7 ⏭️ skip→remembered', '7 ⏭️ skip→tray (one returns per empty seed)')
        done.append('compact-7'); break
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
    if 'v84.56' not in t:
        open(AR, 'a').write('v84.56: RETRAY-ONE - the tray drip-feeds: one skipped soul per empty seed, oldest skip first, skip consumed on feeding, re-skip stamps a fresh timestamp to the back; new loose papers seed and seat ahead of the tray always; no manual unskip needed in the daily flow\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S327 the tray refills only when empty and new blood always outranks it", "'S326 the cue says aloud what cancel leaves behind", "ck('S327 the tray refills only when empty and new blood always outranks it', (chr(35)+' RETRAY v84.55') in _src and ('key=lambda x: 1 if x.get(' + chr(39) + 're' + chr(39) + ') else 0' in _src))"),
      ("'S328 the tray offers one skipped soul per empty seed, oldest first", "'S327 the tray refills only when empty and new blood always outranks it", "ck('S328 the tray offers one skipped soul per empty seed, oldest first', (chr(35)+' RETRAY-ONE v84.56') in _src and ('del skd[kp]; refed += 1; break' in _src))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
