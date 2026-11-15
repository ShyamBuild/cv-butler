import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# CTIME-EYE v81.20' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == "if not hasattr(self, '_tagcrc'): self._tagcrc = {}")
    d = ind(B[i])
    B.insert(i+1, d*' ' + "if not hasattr(self, '_tagct'): self._tagct = {}")
    j = next(k for k, l in enumerate(B) if l.strip() == 'try: tg = _xattr_raw(fp)')
    e = next(k for k in range(j, j+20) if l and B[k].strip().startswith('self._tagsets[fp] = [t for t in'))
    d2 = ind(B[j])
    B[j:e+1] = [d2*' ' + "try: st = os.stat(fp).st_ctime  # CTIME-EYE v81.20: tag writes bump ctime even when the set returns to baseline",
                d2*' ' + "except OSError: st = 0",
                d2*' ' + "tg = _xattr_raw(fp)",
                d2*' ' + "c = _z.crc32(tg)",
                d2*' ' + "oldc = self._tagcrc.get(fp); oldt = self._tagct.get(fp)",
                d2*' ' + "self._tagcrc[fp] = c; self._tagct[fp] = st",
                d2*' ' + "prev = self._tagsets.get(fp)",
                d2*' ' + "if oldc is None and oldt is None:",
                d2*' ' + "    self._tagsets[fp] = [t for t in (_tags_of_fast(fp) or [])]",
                d2*' ' + "elif oldc != c or oldt != st:",
                d2*' ' + "    changed.append(fp)",
                d2*' ' + "    cur = [t for t in (_tags_of_fast(fp) or [])]",
                d2*' ' + "    if prev is not None and not gap:",
                d2*' ' + "        add = [t for t in cur if t not in prev]",
                d2*' ' + "        if not add and cur: add = list(cur)",
                d2*' ' + "        if add: self._added_tags[fp] = add",
                d2*' ' + "    self._tagsets[fp] = cur"]
    done.append('ctime-eye')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S126 the poll sees trace-less tag edits" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S125 re-apply and multi-number draft" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S126 the poll sees trace-less tag edits', (chr(35)+' CTIME-EYE') in _src and 'st_ctime' in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S126-guard')
print('✅', done)
