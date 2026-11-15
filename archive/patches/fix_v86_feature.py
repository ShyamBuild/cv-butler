import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
if 'def _settling(' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.startswith('LOCK_FILE ='))
    B[i+1:i+1] = ["SETTLE_EXTS = ('.crdownload', '.part', '.partial', '.download', '.tmp', '.crdownload ')",
                  "def _settling(p):",
                  "    try:",
                  "        b = os.path.basename(p).lower()",
                  "        if b.endswith(SETTLE_EXTS): return True",
                  "        return (time.time() - os.stat(p).st_mtime) < 20",
                  "    except Exception:",
                  "        return True"]
    done.append('settling-helper')
src = '\n'.join(B)
if 'def _pend(' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def _route(self, p, say):'))
    B[i:i] = ["    def _pend(self, p, say=print):",
              "        if not hasattr(self, '_pending'): self._pending = {}",
              "        self._pending[p] = time.time()",
              "    def _heal(self, say=print):",
              "        if not hasattr(self, '_pending'): self._pending = {}",
              "        if not hasattr(self, '_heal_done'): self._heal_done = {}",
              "        now = time.time()",
              "        for p in [p for p, t in list(self._pending.items()) if now - t > 20 and os.path.exists(p) and not _settling(p)]:",
              "            self._pending.pop(p, None)",
              "            self._route(p, say)",
              "        deb = os.path.join(BASE_DIR, 'download_debris')",
              "        for dp, dn, fn in os.walk(self.root):",
              "            dn[:] = [d for d in dn if not d.startswith('.')]",
              "            for f in fn:",
              "                fp = os.path.join(dp, f); bl = f.lower()",
              "                try: st = os.stat(fp)",
              "                except OSError: continue",
              "                if bl.endswith(SETTLE_EXTS) and now - st.st_mtime > 6 * 3600:",
              "                    os.makedirs(deb, exist_ok=True)",
              "                    try:",
              "                        os.rename(fp, os.path.join(deb, f)); say(f'🧹 debris archived: {f}')",
              "                    except Exception: pass",
              "                    continue",
              "                if not bl.endswith(('.pdf', '.doc', '.docx', '.msg', '.eml', '.xlsx')): continue",
              "                if _settling(fp): continue",
              "                key = f'{fp}|{st.st_mtime_ns}|{st.st_size}'",
              "                if self._heal_done.get(f) == key: continue",
              "                self._heal_done[f] = key",
              "                self._route(fp, say)",
              ""]
    done.append('pend-heal-methods')
src = '\n'.join(B)
if 'if _settling(p): self._pend(p, say); return' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'ext = os.path.splitext(p)[1].lower()' and k > next(j for j, l2 in enumerate(B) if l2.strip().startswith('def _route(self, p, say):')))
    B.insert(i, ind(B[i])*' ' + "if _settling(p): self._pend(p, say); return")
    done.append('route-gate')
if 'def handle_tags(self' in src and '\n'.join(B).count('if _settling(p): return') < 2:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def handle_tags(self'))
    B.insert(i+1, ind(B[i])*' ' + "if _settling(p): return")
    done.append('tags-gate')
src = '\n'.join(B)
if 'if _settling(fp): continue' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'os.rename(fp, dst)')
    B.insert(i, ind(B[i])*' ' + "if _settling(fp): continue")
    done.append('reconcile-gate')
src = '\n'.join(B)
if 'B._heal(hsay)' not in src:
    i = next(k for k, l in enumerate(B) if 'import sem; sem.tick(B)' in l)
    B.insert(i+1, ind(B[i])*' ' + "B._heal(hsay)")
    done.append('heal-wired')
src = '\n'.join(B)
ast.parse(src); open('butler.py', 'w').write(src)
if "'S66 settle-gate on every mutating door" not in src:
    i = next(k for k, l in enumerate(B) if "'S65 chat ctrl-c graceful" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S66 settle-gate on every mutating door', 'def _settling(' in _src and _src.count('_settling(') >= 4)")
    B.insert(i+2, d*' ' + "ck('S67 heal sweep + debris archive', 'def _heal(' in _src and 'download_debris' in _src and 'B._heal(hsay)' in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S66-S67-guards')
print('✅', done)
