import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
old = '        return (time.time() - os.stat(p).st_mtime) < 20'
if old in '\n'.join(B) and 'SETTLE-FAST' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l == old)
    B[i:i+1] = ['        if (time.time() - st.st_mtime) >= 20: return False',
                '        time.sleep(1.5)  # SETTLE-FAST v62: stability beats age',
                '        st2 = os.stat(p)',
                '        return st2.st_size != st.st_size or st2.st_mtime != st.st_mtime']
    done.append('settle-fast')
if 'def _drain_pending(' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def _heal(self, say=print):'))
    B[i:i] = ["    def _drain_pending(self, say=print):",
              "        if not hasattr(self, '_pending'): return",
              "        now = time.time()",
              "        for p in [p for p, t in list(self._pending.items()) if now - t > 3 and os.path.exists(p) and not _settling(p)]:",
              "            self._pending.pop(p, None)",
              "            self._route(p, say)",
              ""]
    done.append('drain-pending-method')
src = '\n'.join(B)
if '# DRAIN-PENDING' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'for p in paths: ex.submit(work, p)')
    B.insert(i+1, ind(B[i])*' ' + 'try: B._drain_pending(print)  # DRAIN-PENDING v62')
    B.insert(i+2, ind(B[i])*' ' + 'except Exception: pass')
    j = next(k for k, l in enumerate(B) if l.strip() == 'for p in _ip: ex.submit(work, p)')
    B.insert(j+1, ind(B[j])*' ' + 'try: B._drain_pending(print)')
    B.insert(j+2, ind(B[j])*' ' + 'except Exception: pass')
    done.append('drain-wired')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S72 settle-fast + pending drain" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S71 rename breaker resets on name change" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S72 settle-fast + pending drain', (chr(35)+' SETTLE-FAST') in _src and (chr(35)+' DRAIN-PENDING') in _src and 'def _drain_pending(' in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S72-guard')
print('✅', done)
