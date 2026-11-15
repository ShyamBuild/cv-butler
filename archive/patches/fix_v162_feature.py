import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if l.strip() == 'if time.time() - lg.get(k, 0) < 60: return':
        B[k] = ind(l)*' ' + "if False and time.time() - lg.get(k, 0) < 60: return  # NEUTER-DEBOUNCE v81.30 (user spec: every tag action is a new event)"
        done.append('neuter-debounce'); break
for k, l in enumerate(B):
    if l.strip().startswith("if kind == 'ctime' and not self._ad_fidget()"):
        B[k] = ind(l)*' ' + "if False and kind == 'ctime': pass  # NEUTER-DONEMARK v81.30 (every tag action is a new event)"
        done.append('neuter-donemark'); break
src = '\n'.join(B)
if '# EVERY-TAG-EVENT v81.30' not in src:
    i1 = next(k for k, l in enumerate(B) if l.strip() == 'if prev is not None and not gap:')
    i2 = next(k for k, l in enumerate(B) if l.strip() == 'if add: self._added_tags[fp] = add')
    d = ind(B[i1])
    B[i1:i2+1] = [d*' ' + "add = list(cur) if cur else []  # EVERY-TAG-EVENT v81.30 (RETOUCH v81.19 superseded): any observed change drafts every tag on the file",
                  d*' ' + "if add: self._added_tags[fp] = add"]
    done.append('every-tag-event')
src = '\n'.join(B)
if '# BASELINE-PERSIST v81.29' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == "if not hasattr(self, '_tag_kind'): self._tag_kind = {}")
    d = ind(B[i])
    B[i+1:i+1] = [d*' ' + "if not getattr(self, '_bp_loaded', False):  # BASELINE-PERSIST v81.29: remember tags across restarts",
                  d*' ' + "    self._bp_loaded = True",
                  d*' ' + "    try:",
                  d*' ' + "        _bl = json.load(open(os.path.join(BASE_DIR, 'tag_baseline.json')))",
                  d*' ' + "        for _p, _v in _bl.items():",
                  d*' ' + "            self._tagcrc[_p] = _v[0]; self._tagct[_p] = _v[1]; self._tagsets[_p] = _v[2]",
                  d*' ' + "        if _bl: print(f'🧠 tag baseline restored: {len(_bl)} files remembered across restart', flush=True)",
                  d*' ' + "    except Exception:",
                  d*' ' + "        pass"]
    c = next(k for k, l in enumerate(B) if '# CTIME-EYE v81.20' in l)
    r = next(k for k in range(c, c+40) if B[k].strip() == 'return changed')
    d2 = ind(B[r])
    B[r:r] = [d2*' ' + "self._bp_n = getattr(self, '_bp_n', 0) + 1",
              d2*' ' + "if self._bp_n % 15 == 1:",
              d2*' ' + "    try:",
              d2*' ' + "        json.dump({p: [self._tagcrc.get(p), self._tagct.get(p), self._tagsets.get(p)] for p in self._tagcrc}, open(os.path.join(BASE_DIR, 'tag_baseline.json'), 'w'))",
              d2*' ' + "    except Exception:",
              d2*' ' + "        pass"]
    done.append('baseline-persist')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S134 the poll remembers across restarts" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S133 one window serves the whole queue" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S134 the poll remembers across restarts', (chr(35)+' BASELINE-PERSIST') in _src and 'tag_baseline.json' in _src)")
    B.insert(i+2, d*' ' + "ck('S135 every tag action is a new event', (chr(35)+' EVERY-TAG-EVENT v81.30') in _src and (chr(35)+' NEUTER-DEBOUNCE') in _src and (chr(35)+' NEUTER-DONEMARK') in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S134-S135-guards')
print('✅', done)
