import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if l.strip().startswith("if tag in cur:") and 'already wears' in l and 'SETTLE' not in l:
        d = ind(l)
        B[k:k+1] = [d*' ' + "drops0 = [t for t in cur if _tag_stage(t) and t != tag]",
                    d*' ' + "if tag in cur and not drops0: say(f'🏷️ {os.path.basename(p)} already wears {tag} - nothing changed'); return  # SETTLE v84.8: but if another stage rides along, the transition still owes its proposal"]
        done.append('settle'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith('if os.path.exists(os.path.join(tgt, os.path.basename(p))): conflict = True'):
        d = ind(l)
        B[k:k+1] = [d*' ' + "_twin = os.path.join(tgt, os.path.basename(p))",
                    d*' ' + "if os.path.exists(_twin): conflict = _twin  # TWIN v84.8: name the twin; the master Bins, the machine never deletes"]
        done.append('twin-name'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("if conflict: txt +=") and 'twin' not in l:
        d = ind(l)
        B[k] = d*' ' + "if conflict: txt += f' · a twin already rests in {tag} ({os.path.relpath(conflict, root)}) - tagged in place; the twin is yours to Bin, I never delete'"
        done.append('twin-text'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S246 a paper wearing two stages still gets its transition proposal", "'S245 papers wearing two stages are named, never silently rewritten", "ck('S246 a paper wearing two stages still gets its transition proposal', (chr(35)+' SETTLE v84.8') in _src)"),
      ("'S247 a name-conflict names the twin and never deletes it", "'S246 a paper wearing two stages still gets its transition proposal", "ck('S247 a name-conflict names the twin and never deletes it', (chr(35)+' TWIN v84.8') in _src and ('yours to Bin' in _src))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
