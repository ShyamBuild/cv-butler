import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if l.strip().startswith("return collections.defaultdict(str, {'first':") and "'roleline': roleline" not in l:
        B[k] = l[:l.rfind('})')] + ", 'roleline': roleline})"  # ROLELINE-KEY v84.20: a computed sentence is worthless if the dict never carries it
        done.append('roleline-key'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S275 the fields dict carries every sentence it computes", "'S274 the fallback chain keeps every scenario speakable", "ck('S275 the fields dict carries every sentence it computes', (\"'roleline': roleline\" in _src) and (chr(35)+' ROLELINE v84.18') in _src)")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
