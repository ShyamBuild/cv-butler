import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# PULSE-WITNESS v81.6' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'return changed' and k > next(j for j, l2 in enumerate(B) if l2.strip() == 'def _tag_poll(self):'))
    d = ind(B[i])
    B.insert(i, d*' ' + "if changed: print(f'🩺 poll changed={len(changed)} added={len(getattr(self, chr(95)+chr(97)+chr(100)+chr(100)+chr(101)+chr(100)+chr(95)+chr(116)+chr(97)+chr(103)+chr(115), {}))}', flush=True)  # PULSE-WITNESS v81.6")
    done.append('poll-witness')
src = '\n'.join(B)
if '# TICK-WITNESS v81.6' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'for fp, tags in added.items():')
    d = ind(B[i])
    B[i:i] = [d*' ' + "if not hasattr(self, '_ad_lastlog'): self._ad_lastlog = 0",
              d*' ' + "if added or q or _t.time() - self._ad_lastlog > 300:",
              d*' ' + "    self._ad_lastlog = _t.time()",
              d*' ' + "    say(f'🩺 autodraft tick: enabled={self._ad_enabled()} mode={mode} adds={len(added)} queue={len(q)}')  # TICK-WITNESS v81.6"]
    done.append('tick-witness')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S114 the pulse has a voice" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S113 every tag-add is witnessed" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S114 the pulse has a voice', (chr(35)+' PULSE-WITNESS') in _src and (chr(35)+' TICK-WITNESS') in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S114-guard')
print('✅', done)
