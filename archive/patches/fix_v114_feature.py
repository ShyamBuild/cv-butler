import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# CLIENT-ROOT v72' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def handle_tags('))
    j = next(k for k in range(i, i+15) if B[k].strip().startswith('T = _tags_of_fast(p)'))
    d = ind(B[j])
    B[j+1:j+1] = [d*' ' + "if len(os.path.relpath(os.path.dirname(p), self.root).split(os.sep)) < 2:  # CLIENT-ROOT v72",
                  d*' ' + "    for t in (T or []):",
                  d*' ' + "        tt = t.replace(chr(8211), '-')",
                  d*' ' + "        if tt in TAG_NAMES or t in TAG_NAMES:",
                  d*' ' + "            nm = re.sub(r'[/\\\\:]', '-', tt)",
                  d*' ' + "            tgt = os.path.join(os.path.dirname(p), nm)",
                  d*' ' + "            os.makedirs(tgt, exist_ok=True)",
                  d*' ' + "            dst = os.path.join(tgt, os.path.basename(p)); c = 1",
                  d*' ' + "            b2, e2 = os.path.splitext(os.path.basename(p))",
                  d*' ' + "            while os.path.exists(dst): dst = os.path.join(tgt, f'{b2}_{c}{e2}'); c += 1",
                  d*' ' + "            if _settling(p): return",
                  d*' ' + "            try:",
                  d*' ' + "                os.rename(p, dst); say(f'📁 [move] {os.path.basename(p)} -> {nm}/ (client root)')",
                  d*' ' + "            except Exception: pass",
                  d*' ' + "            return"]
    done.append('client-root-filing')
src = '\n'.join(B)
if '# HEAL-SNIFF v72' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'self._route(fp, say)')
    d = ind(B[i])
    B[i:i] = [d*' ' + "if '.' not in bl:  # HEAL-SNIFF v72",
              d*' ' + "    _se = _sniff_ext(fp)",
              d*' ' + "    if _se:",
              d*' ' + "        _nb = fp + _se; _n2 = 1",
              d*' ' + "        while os.path.exists(_nb): _nb = f'{fp}_{_n2}{_se}'; _n2 += 1",
              d*' ' + "        try:",
              d*' ' + "            os.rename(fp, _nb); say(f'🧩 [suffix] {os.path.basename(fp)} -> {os.path.basename(_nb)}'); fp = _nb; bl = os.path.basename(_nb).lower()",
              d*' ' + "        except Exception: continue"]
    done.append('heal-sniff')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S92 client-root tag filing" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S91 stranded retry at thirty seconds" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S92 client-root tag filing', (chr(35)+' CLIENT-ROOT') in _src and 'client root)' in _src)")
    B.insert(i+2, d*' ' + "ck('S93 heal sniffs extension-less files', (chr(35)+' HEAL-SNIFF') in _src and _src.count('_sniff_ext(') >= 3)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S92-S93-guards')
print('✅', done)
