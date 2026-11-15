import ast, subprocess
p = 'butler.py'; L = open(p).read().split('\n'); done = []
# 1) rebuild _compact_numbers with correct indentation + canonicalize pass
i = next(k for k, l in enumerate(L) if l.strip().startswith('def _compact_numbers('))
d = len(L[i]) - len(L[i].lstrip())
j = i + 1
while j < len(L) and not (L[j].strip().startswith('def ') and len(L[j]) - len(L[j].lstrip()) == d):
    j += 1
L[i:j] = [d*' ' + 'def _compact_numbers(self, folder, say):',
          d*' ' + '    if not os.path.isdir(folder): return',
          d*' ' + '    for f in sorted(os.listdir(folder)):',
          d*' ' + '        fp = os.path.join(folder, f)',
          d*' ' + '        if not os.path.isfile(fp): continue',
          d*' ' + '        b, e = os.path.splitext(f)',
          d*' ' + "        m = re.match(r'^(.*?)\\s*\\((\\d+)\\)$', b) or re.match(r'^(.*?)\\s+(\\d+)$', b)",
          d*' ' + '        if not m: continue',
          d*' ' + '        base, num = m.group(1).strip(), m.group(2)',
          d*' ' + '        if not base: continue',
          d*' ' + '        target = f"{base}_{num}{e}"',
          d*' ' + '        if target == f: continue',
          d*' ' + '        if os.path.exists(os.path.join(folder, target)): continue',
          d*' ' + "        self._rename(fp, target, say, 'suffix-canonical')",
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
done.append('compact-numbers-rebuilt')
# 2) Ctrl+C dies definitively: os._exit at end of finally
for k, l in enumerate(L):
    if l.strip() == 'try: os.remove(lock_path)' and k+1 < len(L) and L[k+1].strip() == 'except Exception: pass':
        if k+2 >= len(L) or L[k+2].strip() != 'os._exit(0)':
            L.insert(k+2, (len(L[k]) - len(L[k].lstrip()))*' ' + 'os._exit(0)')
            done.append('ctrlc-definitive')
        break
# 3) delete stray module-level reconcile after main()
while L and not L[-1].strip(): L.pop()
if L[-1].strip() == 'except Exception: pass' and len(L) > 1 and L[-2].strip() == 'try: B._reconcile_tags(print)':
    L = L[:-2]; done.append('eof-stray-removed')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done)
r = subprocess.run(['cv_env/bin/python3', '-c', 'import butler; print("IMPORT OK")'], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip()[-300:])
