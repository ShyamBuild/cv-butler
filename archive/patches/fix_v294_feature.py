import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
f0 = next(k for k, l in enumerate(B) if l.startswith('def _find_by_fp('))
f1 = next(k for k in range(f0 + 1, len(B)) if B[k].startswith('def '))
if 'FP-ANY' not in '\n'.join(B[f0:f1]):
    for k in range(f0, f1):
        if B[k].strip().startswith('if not _is_desk_candidate(x): continue'):
            B[k] = ind(B[k])*' ' + "pass  # FP-ANY v84.14: content is identity, extension is only clothing - the fingerprint searches every file"
            done.append('fp-any'); break
src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("say(f'🔁 the paper moved - found it again in") and 'EXT-LOSS' not in '\n'.join(B[k:k+3]):
        d = ind(l)
        B.insert(k+1, d*' ' + "if not p.lower().endswith(('.pdf', '.docx')): say('⚠️ he lost his .pdf/.docx extension in the rename - most doors ignore extension-less papers; rename him back when convenient')  # EXT-LOSS v84.14")
        done.append('ext-loss-warn'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S264 the fingerprint searches every file and names a stripped extension aloud", "'S263 release promotes the waiting chair and never hides a seated secondary", "ck('S264 the fingerprint searches every file and names a stripped extension aloud', (chr(35)+' FP-ANY v84.14') in _src and (chr(35)+' EXT-LOSS v84.14') in _src)")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
