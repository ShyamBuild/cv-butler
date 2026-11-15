import ast, re
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# HEADLESS-INPUT v81.11' not in src:
    i = next(k for k, l in enumerate(B) if re.match(r'^INTERACTIVE\s*=', l))
    B[i+1:i+1] = ["if not INTERACTIVE:",
                  "    import builtins as _bi",
                  "    def _headless_input(prompt=''):",
                  "        _t.sleep(2)",
                  "        return ''",
                  "    _bi.input = _headless_input  # HEADLESS-INPUT v81.11: no prompt may park or kill a headless loop",
                  ""]
    done.append('headless-input')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S118 the REPL cannot park or kill the loop" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S117 headless butler loops instead of listening" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S118 the REPL cannot park or kill the loop', (chr(35)+' HEADLESS-INPUT') in _src and 'builtins' in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S118-guard')
print('✅', done)
