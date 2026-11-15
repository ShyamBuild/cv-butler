import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
n8 = 0
for k, l in enumerate(B):
    if '# TAG-POLL' in l and '> 15:' in l:
        B[k] = l.replace('> 15:', '> 8:'); n8 += 1
if n8: done.append(f'pulse-8s-x{n8}')
src = '\n'.join(B)
if '< 60: continue  # HEAL-RETRY' in src:
    B = [l.replace('< 60: continue  # HEAL-RETRY', '< 30: continue  # HEAL-RETRY') for l in B]
    done.append('heal-retry-30s')
src = '\n'.join(B)
if '# INODE-RELINK v71' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'self.handle_pdf(p, say)')
    d = ind(B[i])
    B[i:i] = [d*' ' + "_ino = None  # INODE-RELINK v71",
              d*' ' + "try: _ino = os.stat(p).st_ino",
              d*' ' + "except Exception: pass"]
    B[i+3:i+3] = [d*' ' + "if _ino is not None and not os.path.exists(p):",
                  d*' ' + "    for _f in os.listdir(os.path.dirname(p)):",
                  d*' ' + "        _c = os.path.join(os.path.dirname(p), _f)",
                  d*' ' + "        try:",
                  d*' ' + "            if os.stat(_c).st_ino == _ino: p = _c; break",
                  d*' ' + "        except Exception: pass"]
    done.append('inode-relink')
src = '\n'.join(B)
if 'def _summary_xlsx(' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def _heal(self, say=print):'))
    B[i:i] = ["    def _summary_xlsx(self, p, say=print):  # SUMMARY-CANON v71",
              "        try:",
              "            b = os.path.basename(p).lower()",
              "            if not b.endswith('.xlsx') or b.startswith('~$'): return p",
              "            import re as _re",
              "            if _re.match(r'summary(_\\d+)?\\.xlsx$', b): return p",
              "            if _settling(p): return p",
              "            import openpyxl",
              "            wb = openpyxl.load_workbook(p, read_only=True, data_only=True)",
              "            ws = wb.active",
              "            hdr = ' | '.join(str(c.value or '').strip() for c in next(ws.iter_rows(min_row=1, max_row=1)))",
              "            wb.close()",
              "            if 'Candidate Name' not in hdr or 'Position' not in hdr: return p",
              "            d = os.path.dirname(p); n = 0",
              "            while True:",
              "                tgt = os.path.join(d, 'Summary.xlsx' if n == 0 else f'Summary_{n}.xlsx')",
              "                if not os.path.exists(tgt): break",
              "                n += 1",
              "                if n > 50: return p",
              "            os.rename(p, tgt); say(f'📊 [summary] {os.path.basename(p)} -> {os.path.basename(tgt)}')",
              "            return tgt",
              "        except Exception:",
              "            return p",
              ""]
    done.append('summary-canon')
src = '\n'.join(B)
if '# SUMMARY-CALL v71' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == "elif ext == '.xlsx':")
    B.insert(i+1, (ind(B[i])+4)*' ' + "p = self._summary_xlsx(p, say)  # SUMMARY-CALL v71")
    done.append('summary-call')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S89 rename and move in one pass" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S88 extension-less files get sniffed" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S89 rename and move in one pass', (chr(35)+' INODE-RELINK') in _src and _src.count('> 8:  ' + chr(35) + ' TAG-POLL') == 2)")
    B.insert(i+2, d*' ' + "ck('S90 summary xlsx canon everywhere', (chr(35)+' SUMMARY-CANON') in _src and (chr(35)+' SUMMARY-CALL') in _src and 'def _summary_xlsx(' in _src)")
    B.insert(i+3, d*' ' + "ck('S91 stranded retry at thirty seconds', (chr(60)+' 30: continue  '+chr(35)+' HEAL-RETRY') in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S89-S91-guards')
print('✅', done)
