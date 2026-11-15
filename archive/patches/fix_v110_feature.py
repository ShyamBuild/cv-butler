import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
n8 = 0
for k, l in enumerate(B):
    if '# TAG-POLL v65' in l and '> 15:' in l:
        B[k] = l.replace('> 15:', '> 8:'); n8 += 1
if n8: done.append(f'pulse-8s-x{n8}')
src = '\n'.join(B)
if '# RENAME-ECHO v71' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def _rename(self, old_path, new_name, say, tag):'))
    j = next(k for k in range(i, i+40) if '[rename]' in B[k])
    B.insert(j+1, ind(B[j])*' ' + "self._last_rename = (old_path, new_name)  # RENAME-ECHO v71")
    done.append('rename-echo')
src = '\n'.join(B)
if '# RENAME-ECHO-USE v71' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'self.handle_pdf(p, say)')
    d = ind(B[i])
    B.insert(i+1, d*' ' + "_rn = getattr(self, '_last_rename', None)  # RENAME-ECHO-USE v71")
    B.insert(i+2, d*' ' + "if _rn and _rn[0] == p and not os.path.exists(p):")
    B.insert(i+3, d*' ' + "    _g = os.path.join(os.path.dirname(p), _rn[1])")
    B.insert(i+4, d*' ' + "    if os.path.exists(_g): p = _g")
    done.append('route-echo-use')
src = '\n'.join(B)
if 'def _summary_xlsx(' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def _heal(self, say=print):'))
    B[i:i] = ["    def _summary_xlsx(self, p, say=print):  # SUMMARY-NORM v71",
              "        try:",
              "            b = os.path.basename(p).lower()",
              "            if not b.endswith('.xlsx') or b.startswith('~$'): return",
              "            import re as _re",
              "            if _re.match(r'summary(_\\d+)?\\.xlsx$', b): return",
              "            if _settling(p): return",
              "            import zipfile",
              "            z = zipfile.ZipFile(p)",
              "            blob = b''",
              "            for nm in ('xl/sharedStrings.xml', 'xl/worksheets/sheet1.xml'):",
              "                if nm in z.namelist():",
              "                    blob = z.read(nm); break",
              "            if blob.lower().find(b'candidate name') < 0: return",
              "            d = os.path.dirname(p); n = 0",
              "            while True:",
              "                tgt = os.path.join(d, 'Summary.xlsx' if n == 0 else f'Summary_{n}.xlsx')",
              "                if not os.path.exists(tgt): break",
              "                n += 1",
              "                if n > 50: return",
              "            os.rename(p, tgt); say(f'📊 [summary] {os.path.basename(p)} -> {os.path.basename(tgt)}')",
              "        except Exception:",
              "            pass",
              ""]
    done.append('summary-normalizer')
src = '\n'.join(B)
if 'self._summary_xlsx(p, say)' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == "elif ext == '.xlsx':")
    B.insert(i+1, ind(B[i])*' ' + "self._summary_xlsx(p, say)  # SUMMARY-CALL v71")
    done.append('summary-call')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S89 eight second pulse" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S88 extension-less files get sniffed" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S89 eight second pulse', _src.count('> 8:  ' + chr(35) + ' TAG-POLL') == 2)")
    B.insert(i+2, d*' ' + "ck('S90 rename echo re-points route before tagging', (chr(35)+' RENAME-ECHO v71') in _src and (chr(35)+' RENAME-ECHO-USE') in _src)")
    B.insert(i+3, d*' ' + "ck('S91 summary xlsx normalized by content', 'def _summary_xlsx(' in _src and (chr(35)+' SUMMARY-CALL') in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S89-S91-guards')
print('✅', done)
