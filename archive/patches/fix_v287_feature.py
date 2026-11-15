import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'taught_digits(' in src:
    defs = re.findall(r'^def (\w+)\(', src, re.M)
    cand = [n for n in defs if ('taught' in n or 'digits' in n or 'book' in n) and n != 'taught_digits']
    if cand:
        real = cand[0]
        src = src.replace('taught_digits(', real + '(')
        done.append('phone-repoint:' + real)
    else:
        i = next(k for k, l in enumerate(B) if l.startswith('def calls_cmd('))
        helper = ["def taught_digits(name):  # CHAIR-PHONE v84.10c: the chair reads the taught book directly, then falls back to the paper",
                  "    import json as _j",
                  "    low = (name or '').lower()",
                  "    for fn in ('taught.json', 'phonebook.json', 'taught_book.json', 'phones.json'):",
                  "        lp = os.path.join(BASE_DIR, fn)",
                  "        if not os.path.exists(lp): continue",
                  "        try: d = _j.load(open(lp))",
                  "        except Exception: continue",
                  "        if isinstance(d, dict):",
                  "            for k, v in d.items():",
                  "                kl = str(k).lower()",
                  "                if low and (low in kl or kl in low):",
                  "                    if isinstance(v, list): return v",
                  "                    if isinstance(v, str) and v.strip().isdigit(): return v.strip()",
                  "        break",
                  "    return None",
                  ""]
        B[i:i] = helper
        src = '\n'.join(B)
        done.append('phone-reader-installed')
    src = '\n'.join(B) if not cand else src
    ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S254 no ghost may name the phone book", "'S253 the sheet advances only after a confirmed outcome", "ck('S254 no ghost may name the phone book', ('taught_' + 'digits(' not in _src.replace('def taught_digits(', 'DEF')) or ('def taught_digits(' in _src))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
