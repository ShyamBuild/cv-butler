import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# LOG-FLUSH v81.8' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('import '))
    B[i:i] = ["try:",
              "    import sys as _sysio; _sysio.stdout.reconfigure(line_buffering=True)  # LOG-FLUSH v81.8",
              "except Exception:",
              "    pass"]
    done.append('log-flush')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S116 the log speaks instantly" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S115 tags read through macOS libc" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S116 the log speaks instantly', (chr(35)+' LOG-FLUSH') in _src and 'line_buffering' in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S116-guard')
print('✅', done)
