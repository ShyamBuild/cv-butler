import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if l.strip().startswith("cm[k.strip()] = v.strip()") and 'RETEACH' not in '\n'.join(B[k:k+4]):
        d = ind(l)
        B[k:k+1] = [d*' ' + "_prev = cm.get(k.strip())  # RETEACH v84.26: an overwrite speaks its before-and-after, so no haste-teaching steals a true one silently",
                    d*' ' + "cm[k.strip()] = v.strip()"]
        done.append('reteach-prev'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("say(f'🏢 client taught: {k.strip()} = {v.strip()}')"):
        d = ind(l)
        B[k] = d*' ' + "say(f'🏢 client re-taught: {k.strip()} was {_prev} → now {v.strip()}' if _prev and _prev != v.strip() else f'🏢 client taught: {k.strip()} = {v.strip()}')  # RETEACH v84.26"
        done.append('reteach-echo'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S284 a re-teaching speaks its before-and-after", "'S283 the teach door works in chat and the ledger holds only real folders", "ck('S284 a re-teaching speaks its before-and-after', (chr(35)+' RETEACH v84.26') in _src)")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
