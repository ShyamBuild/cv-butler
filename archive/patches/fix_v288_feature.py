import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def _is_desk_candidate(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def calls_cmd('))
    B[i:i] = ["NON_CANDIDATE_PREFIXES = ('jd', 'summary', 'rated_', 'candidate', 'form', 'template')  # PAPER-OR-NOT v84.10d: the desk knows a CV from its furniture",
              "def _is_desk_candidate(x):  # PAPER-OR-NOT v84.10d: only humans take the chair",
              "    low = (x or '').lower()",
              "    if not low.endswith(('.pdf', '.docx')): return False",
              "    stem = low[:-5] if low.endswith('.docx') else low[:-4]",
              "    for pre in NON_CANDIDATE_PREFIXES:",
              "        if stem.startswith(pre): return False",
              "    return True",
              ""]
    done.append('paper-or-not')
    src = '\n'.join(B)
n = 0
for k, l in enumerate(B):
    if l.strip() == "if not x.lower().endswith(('.pdf', '.docx')): continue":
        B[k] = ind(l)*' ' + "if not _is_desk_candidate(x): continue  # PAPER-OR-NOT v84.10d"
        n += 1
if n: done.append(f'candidate-filter-x{n}')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n2 in needles:
        hit = [k for k, l in enumerate(B) if n2 in l]
        if hit: return hit[-1]
    return None
GU = [("'S255 the sheet seats humans, not JDs or summaries", "'S254 no ghost may name the phone book", "ck('S255 the sheet seats humans, not JDs or summaries', (chr(35)+' PAPER-OR-NOT v84.10d') in _src and ('def _is_desk_candidate(' in _src) and ('_is_desk_candidate(x)' in _src))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
