import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
W = open('wa.py').read().split('\n')
out = []; k = 0
while k < len(W):
    out.append(W[k])
    s = W[k].strip()
    if s in ('_arm(digits, text)', 'if sent: _arm(digits, text)') and k+1 < len(W) and W[k+1].strip() == s:
        k += 1
        done.append('wa-arm-dedupe')
    k += 1
open('wa.py', 'w').write('\n'.join(out))
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def handle_pdf(self, p, say):' in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'def handle_pdf(self, p, say):')
    B[i] = ind(B[i])*' ' + 'def handle_pdf(self, p, say, quick=False):'
    j = next(k for k in range(i, i+80) if B[k].strip() == 'if not text.strip():')
    B.insert(j, ind(B[j])*' ' + 'if quick and not text.strip(): return  # QUICK-RENAME v65')
    done.append('quick-rename-param')
src = '\n'.join(B)
if 'self.handle_pdf(p, say, quick=True)' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'self.handle_pdf(p, say)')
    B[i] = ind(B[i])*' ' + 'self.handle_pdf(p, say, quick=True)'
    done.append('route-quick')
if '# TAGS-FIRST v63' in src:
    i = next(k for k, l in enumerate(B) if '# TAGS-FIRST v63' in l)
    del B[i]
    done.append('protocol-restore-rename-then-move')
src = '\n'.join(B)
if '# RENAME-FIRST v65' not in src:
    i = next(k for k, l in enumerate(B) if '# RECONCILE-GATE v60' in l)
    B[i+1:i+1] = [ind(B[i])*' ' + 'self.handle_pdf(fp, say, quick=True)  # RENAME-FIRST v65',
                  ind(B[i])*' ' + 'if not os.path.exists(fp): continue']
    done.append('reconcile-rename-first')
src = '\n'.join(B)
if '# FULL-RENAME v65' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def _heal(self, say=print):'))
    j = next(k for k in range(i, i+40) if B[k].strip() == 'self._route(fp, say)')
    B.insert(j, ind(B[j])*' ' + "if fp.lower().endswith('.pdf'): self.handle_pdf(fp, say)  # FULL-RENAME v65")
    done.append('heal-full-rename')
src = '\n'.join(B)
if '# HEAL-RETRY v65' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'if self._heal_done.get(f) == key: continue')
    d = ind(B[i])
    B[i:i+2] = [d*' ' + 'prev = self._heal_done.get(f)',
                d*' ' + 'if prev and prev[0] == key and now - prev[1] < 600: continue  # HEAL-RETRY v65',
                d*' ' + 'self._heal_done[f] = (key, now)']
    done.append('heal-retry-expiry')
src = '\n'.join(B)
if '# SUFFIX-STABLE v65' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'if name and f"{name}.pdf" != base:')
    d = ind(B[i])
    B[i:i+1] = [d*' ' + "_b0 = os.path.splitext(base)[0]  # SUFFIX-STABLE v65",
                d*' ' + "_okb = (not name) or _b0.lower() == name.lower() or bool(re.match(re.escape(name) + r'[_\\s]\\d+$', _b0, re.I))",
                d*' ' + "if name and not _okb:"]
    done.append('suffix-stable')
src = '\n'.join(B)
if '# SELF-FREE v65' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def _rename(self, old_path, new_name, say, tag):'))
    d = ind(B[i]) + 4
    B[i+1:i+1] = [d*' ' + "_selfb = os.path.basename(old_path).lower()  # SELF-FREE v65",
                  d*' ' + "_bn, _be = os.path.splitext(new_name)",
                  d*' ' + "if (_bn + _be).lower() == _selfb: return  # SELF-FREE v65"]
    done.append('self-free')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if l.strip().startswith("ck('S73 "):
        B[k] = ind(l)*' ' + "ck('S73 fast xattr tag reads + protocol order', 'def _has_tag_xattr(' in _src and 'def _tags_of_fast(' in _src and (chr(35)+' TAGS-FIRST') not in _src)"
        done.append('S73-evolved'); break
if "'S77 PROTOCOL rename-then-move for CVs" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S76 reconcile reads tags without mdls" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "_pdfseg = _src.split(\"elif ext == '.pdf':\")[1].split('elif ext ==')[0]")
    B.insert(i+2, d*' ' + "ck('S77 PROTOCOL rename-then-move for CVs', _pdfseg.index('self.handle_pdf(') < _pdfseg.index('self.handle_tags(') and (chr(35)+' TAGS-FIRST') not in _pdfseg)")
    B.insert(i+3, d*' ' + "ck('S78 heal retries + reconcile rename-first', (chr(35)+' HEAL-RETRY') in _src and (chr(35)+' RENAME-FIRST') in _src)")
    B.insert(i+4, d*' ' + "ck('S79 suffix-stable renames, self slot free', (chr(35)+' SUFFIX-STABLE') in _src and _src.count(chr(35)+' SELF-FREE') >= 2)")
    B.insert(i+5, d*' ' + "ck('S80 one ack clock per send', _wa.count('_arm(digits, text)') == 2)")
    B.insert(i+6, d*' ' + "ck('S81 hybrid: cheap rename now, OCR rename in heal', 'quick=False' in _src and (chr(35)+' QUICK-RENAME') in _src and (chr(35)+' FULL-RENAME') in _src and _src.count('quick=True') >= 2)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S77-S81-guards')
print('✅', done)
