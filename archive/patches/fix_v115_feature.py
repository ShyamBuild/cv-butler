import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# CLIENT-ROOT v73' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('if len(os.path.relpath(os.path.dirname(p), self.root)') and '# CLIENT-ROOT' not in l and l.strip().endswith('return'))
    d = ind(B[i])
    B[i:i] = [d*' ' + "if len(os.path.relpath(os.path.dirname(p), self.root).split(os.sep)) < 2:  # CLIENT-ROOT v73",
              d*' ' + "    for t in ((_tags_of_fast(p) or get_tags(p)) or []):",
              d*' ' + "        tt = t.replace(chr(8211), '-')",
              d*' ' + "        if tt in TAG_NAMES or t in TAG_NAMES:",
              d*' ' + "            nm = re.sub(r'[/\\\\:]', '-', tt)",
              d*' ' + "            tgt = os.path.join(os.path.dirname(p), nm)",
              d*' ' + "            os.makedirs(tgt, exist_ok=True)",
              d*' ' + "            dst = os.path.join(tgt, os.path.basename(p)); c = 1",
              d*' ' + "            b2, e2 = os.path.splitext(os.path.basename(p))",
              d*' ' + "            while os.path.exists(dst): dst = os.path.join(tgt, f'{b2}_{c}{e2}'); c += 1",
              d*' ' + "            if _settling(p): return",
              d*' ' + "            try:",
              d*' ' + "                os.rename(p, dst); say(f'📁 [move] {os.path.basename(p)} -> {nm}/ (client root)')",
              d*' ' + "            except Exception: pass",
              d*' ' + "            return"]
    done.append('client-root-top')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S94 client-root block on live path" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S93 heal sniffs extension-less files" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S94 client-root block on live path', _src.index(chr(35)+' CLIENT-ROOT v73') < _src.index('def handle_tags') + 900 and _src.index(chr(35)+' CLIENT-ROOT v73') < _src.split(chr(35)+' CLIENT-ROOT v73')[0].count('return') * 0 + _src.index('split(os.sep)) < 2: return'))")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S94-guard')
print('✅', done)
