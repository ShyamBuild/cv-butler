import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if "[rename-clean]" in l and "say(f'✏️" in l:
        if B[k+1].strip() == 'except Exception:' and B[k+2].strip() == 'pass':
            B[k+1] = ind(B[k+1])*' ' + "except Exception as _rce2:"
            B[k+2] = ind(B[k+2])*' ' + "say(f'⚠️[rename-clean] could not rename {f}: {_rce2}')  # RENAME-LOUD v81.51: a failed heal is a wound, not a silence"
            done.append('rename-error-speaks'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S163 a failed rename speaks its reason" not in '\n'.join(B):
    anch = [k for k, l in enumerate(B) if "'S162 scars born in a scan are cleaned in the same scan" in l]
    i = anch[-1]; d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S163 a failed rename speaks its reason', (chr(35)+' RENAME-LOUD v81.51') in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S163-guard')
print('✅', done)
