import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if "[rename-clean]" in l and "say(f'✏️" in l:
        if B[k+1].strip() == 'except Exception:' and B[k+2].strip() == 'pass':
            d = ind(B[k+1])
            B[k+1] = d*' ' + "except Exception as _rce2:"
            B[k+2] = d*' ' + "say(f'⚠️[rename-clean] could not rename {f}: {_rce2}')  # RENAME-LOUD v81.51: a failed heal is a wound, not a silence"
            done.append('rename-error-speaks'); break
B = [l for l in B if '# DASH-CLEAN-PASS2 v81.50' not in l and 'rename-clean pass 2 skipped' not in l]
src = '\n'.join(B)
if '# RENAMED-PLACE v81.51' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('_console_start()'))
    d = ind(B[i])
    B[i:i] = [d*' ' + "try: B._rename_clean()  # DASH-CLEAN-PASS2 v81.50 # RENAMED-PLACE v81.51: after every convert/reconcile, before the console opens",
              d*' ' + "except Exception as _rc2e: print(f'⚠️ rename-clean pass 2 skipped: {_rc2e}', flush=True)"]
    done.append('pass2-relocated')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S163 a failed rename speaks its reason" not in '\n'.join(B):
    anch = [k for k, l in enumerate(B) if "'S162 scars born in a scan are cleaned in the same scan" in l]
    i = anch[-1]; d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S163 a failed rename speaks its reason', (chr(35)+' RENAME-LOUD v81.51') in _src and (chr(35)+' RENAMED-PLACE v81.51') in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S163-guard')
print('✅', done)
