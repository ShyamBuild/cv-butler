import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# AD-VISIBILITY v81.1' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'if not self._ad_enabled(): return')
    d = ind(B[i])
    B[i:i+1] = [d*' ' + "try: st = open(os.path.join(BASE_DIR, 'autodraft.flag')).read().strip() or 'auto'",
                d*' ' + "except Exception: st = 'auto'",
                d*' ' + "if not self._ad_enabled():",
                d*' ' + "    if getattr(self, '_added_tags', None):",
                d*' ' + "        n = sum(len(v) for v in self._added_tags.values())",
                d*' ' + "        if n: say(f'🔕 autodraft off (flag={st}) - {n} tag-add(s) ignored')  # AD-VISIBILITY v81.1",
                d*' ' + "        self._added_tags = {}",
                d*' ' + "    return"]
    done.append('tick-visibility')
src = '\n'.join(B)
old = '            if len(rel) < 2: return'
if old in src and 'no position folder' not in src:
    i = next(k for k, l in enumerate(B) if l == old)
    B[i] = ind(B[i])*' ' + "if len(rel) < 2: say(f'⏭️ autodraft skip (no position folder): {os.path.basename(fp)}'); return"
    done.append('depth-visibility')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S109 autodraft silence explains itself" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S108 drafts go through the signed wa door" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S109 autodraft silence explains itself', (chr(35)+' AD-VISIBILITY') in _src and 'no position folder' in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S109-guard')
print('✅', done)
