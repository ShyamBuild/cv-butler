import ast
p = 'butler.py'; L = open(p).read().split('\n'); done = []
# 1) canonicalize space/paren suffixes -> _N inside _compact_numbers
if 'suffix-canonical' not in '\n'.join(L):
    a = next(k for k, l in enumerate(L) if l.strip().startswith('def _compact_numbers('))
    d = len(L[a]) - len(L[a].lstrip())
    j = a + 1
    while j < len(L) and not L[j].strip().startswith('for f in sorted(os.listdir(folder)):'):
        j += 1
    L[j:j] = [d*' ' + 'for f in sorted(os.listdir(folder)):',
              d*' ' + '    fp = os.path.join(folder, f)',
              d*' ' + '    if not os.path.isfile(fp): continue',
              d*' ' + '    b, e = os.path.splitext(f)',
              d*' ' + "    m = re.match(r'^(.*?)\\s*\\((\\d+)\\)$', b) or re.match(r'^(.*?)\\s+(\\d+)$', b)",
              d*' ' + '    if not m: continue',
              d*' ' + '    base, num = m.group(1).strip(), m.group(2)',
              d*' ' + '    if not base: continue',
              d*' ' + '    target = f"{base}_{num}{e}"',
              d*' ' + '    if target == f: continue',
              d*' ' + '    if os.path.exists(os.path.join(folder, target)): continue',
              d*' ' + "    self._rename(fp, target, say, 'suffix-canonical')",
              '']
    done.append('suffix-canonical-pass')
# 2) run compaction on every pdf/xlsx route so the tree converges fast
for i, l in enumerate(L):
    if l.strip() == "if not getattr(self, '_skip_tags', False): self.handle_tags(p, say)" and i+1 < len(L) and '_compact_numbers' not in L[i+1]:
        d = len(l) - len(l.lstrip())
        L.insert(i+1, d*' ' + 'self._compact_numbers(os.path.dirname(p), say)')
        done.append('route-compacts-pdf')
        break
for i, l in enumerate(L):
    if l.strip() == "if not getattr(self, '_skip_tags', False): self.handle_tags(p, say)" and i+1 < len(L) and '_compact_numbers' not in L[i+1] and L[i-2].strip().startswith('self.handle_excel'):
        d = len(l) - len(l.lstrip())
        L.insert(i+1, d*' ' + 'self._compact_numbers(os.path.dirname(p), say)')
        done.append('route-compacts-xlsx')
        break
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done or 'nothing missing')
