import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'if st.st_size == 0: return True' not in src and 'def _settling(' in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'if b.endswith(SETTLE_EXTS): return True')
    B.insert(i+1, ind(B[i])*' ' + 'st = os.stat(p)')
    B.insert(i+2, ind(B[i])*' ' + 'if st.st_size == 0: return True')
    done.append('settling-zero-size')
if '# RENAME-GATE v61' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def _rename(self, old_path, new_name, say, tag):'))
    B.insert(i+1, (ind(B[i])+4)*' ' + 'if _settling(old_path): return  # RENAME-GATE v61')
    done.append('rename-gated')
if '# NORM-GATE v61' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def normalize_suffix(self, p, say):'))
    B.insert(i+1, (ind(B[i])+4)*' ' + 'if _settling(p): return p  # NORM-GATE v61')
    done.append('normalize-gated')
src = '\n'.join(B)
if 'while os.path.exists(dst): dst = os.path.join(tgt,' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'if os.path.exists(dst): continue')
    d = ind(B[i])
    B[i:i+1] = [d*' ' + 'if os.path.exists(dst):',
                d*' ' + '    b2, e2 = os.path.splitext(f); c2 = 1',
                d*' ' + '    while os.path.exists(dst): dst = os.path.join(tgt, f"{b2}_{c2}{e2}"); c2 += 1']
    done.append('reconcile-dedupe')
if 'self.rcn' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.strip().startswith('if ino is not None and self.rc.get(ino, 0) >= 2:'))
    d = ind(B[i])
    B.insert(i, d*' ' + "if ino is not None and getattr(self, 'rcn', {}).get(ino) != base:")
    B.insert(i+1, d*' ' + "    self.rcn = getattr(self, 'rcn', {}); self.rcn[ino] = base; self.rc[ino] = 0")
    done.append('rc-reset-on-rename')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S69 rename hands gated" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S68 selftest opens settle-gates" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S69 rename hands gated', (chr(35)+' RENAME-GATE') in _src and (chr(35)+' NORM-GATE') in _src)")
    B.insert(i+2, d*' ' + "ck('S70 reconcile dedupes instead of skipping', 'while os.path.exists(dst): dst = os.path.join(tgt,' in _src.split('def _reconcile_tags')[1].split('def ')[0])")
    B.insert(i+3, d*' ' + "ck('S71 rename breaker resets on name change', 'self.rcn' in _src.split('def handle_pdf')[1].split('def ')[0])")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S69-S71-guards')
print('✅', done)
