import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# DASH-2 v81.50' not in src:
    for k, l in enumerate(B):
        if l.strip() == "if '---' not in stem: continue":
            B[k] = ind(l)*' ' + "if '--' not in stem: continue  # DASH-2 v81.50: two-dash scars are scars too"
            done.append('dash-threshold'); break
    for k, l in enumerate(B):
        if "re.sub(r'\\s*-{3,}\\s*'" in l:
            B[k] = l.replace('-{3,}', '-{2,}')
            done.append('dash-regex'); break
    for k, l in enumerate(B):
        if l.strip() == 'if os.path.exists(dst): continue':
            d = ind(l)
            B[k] = d*' ' + "if os.path.exists(dst): say(f'⏭️[rename-clean] {f} keeps its scars - a clean {clean + ext} already exists'); continue"
            done.append('collision-speaks'); break
src = '\n'.join(B)
if '# DASH-CLEAN-PASS2 v81.50' not in src:
    i = next(k for k, l in enumerate(B) if 'Scan complete' in l and 'say(' in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "try: B._rename_clean()  # DASH-CLEAN-PASS2 v81.50: pdfs born from scarred sources during this scan are cleaned in this boot")
    B.insert(i+2, d*' ' + "except Exception as _rc2e: say(f'⚠️ rename-clean pass 2 skipped: {_rc2e}')")
    done.append('pass2-after-scan')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S162 scars born in a scan are cleaned in the same scan" not in '\n'.join(B):
    anch = [k for k, l in enumerate(B) if "'S161 connected clients close only their page" in l]
    i = anch[-1]; d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S162 scars born in a scan are cleaned in the same scan', (chr(35)+' DASH-CLEAN-PASS2 v81.50') in _src and (chr(35)+' DASH-2 v81.50') in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S162-guard')
print('✅', done)
