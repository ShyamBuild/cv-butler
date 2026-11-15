import ast, re as _re
done = []
def ind(l): return len(l) - len(l.lstrip())
FN = ["def _clean_stem(stem):  # SCAR-WIDE v81.59 + v81.62: brackets, portal glue, resume-words and date-stamps are download scars too",
      "    s = re.sub(r'\\[[^\\]]*\\]', ' ', stem)",
      "    s = re.sub(r'\\(\\d+\\)', ' ', s)",
      "    s = re.sub(r'^(naukri|linkedin|indeed|shine|monster|cutshort)[_\\-]', '', s, flags=re.I)",
      "    s = re.sub(r'\\s*-{2,}\\s*', ' ', s)",
      "    for _i in (0, 1):",
      "        s = re.sub(r'\\b(resume|updated|copy|final|cv)\\b', ' ', s, flags=re.I)",
      "        s = re.sub(r'\\d{2}\\.\\d{2}\\.\\d{4}', ' ', s)",
      "        s = re.sub(r'[_\\-]\\d{2,4}(?=$|\\s)', ' ', s)",
      "        s = re.sub(r'_{2,}', ' ', s)",
      "        s = re.sub(r'(?<=[A-Za-z0-9])_(?=[A-Za-z0-9])', ' ', s)",
      "        s = re.sub(r'\\s[_\\-\\.]|[_\\-\\.]\\s', ' ', s)",
      "        s = re.sub(r'\\s{2,}', ' ', s)",
      "    s = s.strip(' ._-')",
      "    if s.replace('.', '').replace(' ', '').isupper(): s = s.title()",
      "    return s",
      ""]
B = open('butler.py').read().split('\n')
hit = [k for k, l in enumerate(B) if l.startswith('def _clean_stem(')]
if hit:
    e = next(k for k in range(hit[0], len(B)) if B[k].strip() == 'return s')
    B[hit[0]:e+1] = FN[:-1]
    done.append('clean-stem-hardened')
else:
    i = next(k for k, l in enumerate(B) if l.startswith('def phones_of(p):'))
    B[i:i] = FN
    done.append('clean-stem-hardened')
src = '\n'.join(B)
if '# SCAR-WIDE v81.59 gate' not in src:
    for k, l in enumerate(B):
        if l.strip().startswith("if '--' not in stem: continue"):
            dd = ind(l)
            B[k:k+1] = [dd*' ' + "_sc = bool(re.search(r'--|\\[|\\(|[A-Za-z]_[A-Za-z0-9]|\\d{2}\\.\\d{2}\\.\\d{4}', stem)) or bool(re.search(r'\\b(resume|updated|copy|final|cv)\\b', stem, re.I))",
                        dd*' ' + "if not _sc: continue  # DASH-2 v81.50 + SCAR-WIDE v81.59 gate: any visible scar fires the heal"]
            done.append('scar-wide-gate'); break
    for k, l in enumerate(B):
        if l.strip().startswith('clean = re.sub') and '-{2,}' in l:
            B[k] = ind(l)*' ' + "clean = _clean_stem(stem)"
            done.append('clean-stem-call'); break
_ns = {'re': _re}
exec(compile('\n'.join(FN), 'clean_stem_probe', 'exec'), _ns)
for _s in ['Naukri_Himagirisha[3y_9m]', 'Resume Sanjeev Kumar Updated_12.08.2026', 'Prateek Tyagi_CV_2026', 'Praveenkumar K']:
    print('DIAG', repr(_s), '->', repr(_ns['_clean_stem'](_s)))
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S169 brackets and portal glue are scars too" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S168 pincodes never lend digits to phones" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S169 brackets and portal glue are scars too', _clean_stem('Naukri_Himagirisha[3y_9m]') == 'Himagirisha' and _clean_stem('Resume Sanjeev Kumar Updated_12.08.2026') == 'Sanjeev Kumar' and _clean_stem('Prateek Tyagi_CV_2026') == 'Prateek Tyagi' and _clean_stem('Praveenkumar K') == 'Praveenkumar K')")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S169-guard')
print('✅', done)
