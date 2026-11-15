import ast
p = 'butler.py'; L = open(p).read().split('\n'); done = []
if not any(l.strip().startswith('def _compact_numbers(') for l in L):
    a = next(k for k, l in enumerate(L) if l.strip().startswith('def _check_siblings('))
    d = len(L[a]) - len(L[a].lstrip())
    L[a:a] = [d*' ' + 'def _compact_numbers(self, folder, say):',
              d*' ' + '    if not os.path.isdir(folder): return',
              d*' ' + '    for f in sorted(os.listdir(folder)):',
              d*' ' + '        if f.lower().endswith(".pdf"):',
              d*' ' + '            try: self.normalize_suffix(os.path.join(folder, f), say)',
              d*' ' + '            except Exception: pass',
              d*' ' + '    fam = {}',
              d*' ' + '    for f in sorted(os.listdir(folder)):',
              d*' ' + '        fp = os.path.join(folder, f)',
              d*' ' + '        if not os.path.isfile(fp) or f.lower().endswith(".pdf"): continue',
              d*' ' + '        b, e = os.path.splitext(f)',
              d*' ' + "        m = re.match(r'^(.*?)[ _](\\d+)$', b) or re.match(r'^(.*?)\\((\\d+)\\)$', b)",
              d*' ' + '        key = ((m.group(1).strip() if m else b), e.lower())',
              d*' ' + '        fam.setdefault(key, []).append((0 if not m else int(m.group(2)), f))',
              d*' ' + '    for (base, e), items in fam.items():',
              d*' ' + '        if base.lower() in self.locks: continue',
              d*' ' + '        numbered = sorted([(n, f) for n, f in items if n])',
              d*' ' + '        if not numbered: continue',
              d*' ' + '        plain = os.path.join(folder, base + e)',
              d*' ' + '        if not os.path.exists(plain):',
              d*' ' + '            n0, f0 = numbered[0]',
              d*' ' + '            self._rename(os.path.join(folder, f0), base + e, say, "compact")',
              d*' ' + '        cur = {}',
              d*' ' + '        for f in os.listdir(folder):',
              d*' ' + '            b2, e2 = os.path.splitext(f)',
              d*' ' + "            m2 = re.match(r'^(.*?)[ _](\\d+)$', b2) or re.match(r'^(.*?)\\((\\d+)\\)$', b2)",
              d*' ' + '            if m2 and m2.group(1).strip() == base and e2.lower() == e:',
              d*' ' + '                cur[int(m2.group(2))] = f',
              d*' ' + '        for expect in range(1, len(cur) + 1):',
              d*' ' + '            if expect in cur: continue',
              d*' ' + '            act = min((x for x in cur if x > expect), default=None)',
              d*' ' + '            if act is None: break',
              d*' ' + '            self._rename(os.path.join(folder, cur[act]), f"{base}_{expect}{e}", say, "compact")',
              d*' ' + '            del cur[act]; cur[expect] = f"{base}_{expect}{e}"',
              '']
    done.append('compact-numbers-added')
for i, l in enumerate(L):
    if l.strip().startswith('def _check_siblings('):
        j = i + 1
        while j < len(L) and (not L[j].strip() or (len(L[j]) - len(L[j].lstrip())) > (len(L[i]) - len(L[i].lstrip()))):
            j += 1
        d = len(L[i]) - len(L[i].lstrip())
        L[i:j] = [d*' ' + 'def _check_siblings(self, folder):',
                  d*' ' + '    try:',
                  d*' ' + '        self._compact_numbers(folder, print)',
                  d*' ' + '    except Exception:',
                  d*' ' + '        pass',
                  '']
        done.append('check-siblings-compacts'); break
for i, l in enumerate(L):
    if l.strip() == "self._rename(p, \"Summary.xlsx\", say, 'excel')":
        d = len(l) - len(l.lstrip())
        L.insert(i+1, d*' ' + 'self._compact_numbers(os.path.dirname(p), say)')
        done.append('excel-compacts'); break
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done or 'nothing missing')
