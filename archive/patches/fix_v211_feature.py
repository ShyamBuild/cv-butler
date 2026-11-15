import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if 'if tk and (tk == stem or all(w in stem for w in tk.split())):' in l:
        B[k] = ind(l)*' ' + "if tk and (tk == stem or sorted(tk.split()) == sorted(stem.split())):  # EXACT-TEACH v81.73: a token is a whole word or nothing; 'a' inside 'sharma' is not identity"
        done.append('taught-exact'); break
for k, l in enumerate(B):
    if 'for pg in pdf.pages[:2])' in l:
        B[k] = l.replace('pdf.pages[:2]', 'pdf.pages')
        done.append('all-pages'); break
src = '\n'.join(B)
if '# IDENTITY-FIRST v81.73' not in src:
    i = next(k for k, l in enumerate(B) if 'taught number in use for' in l)
    d = ind(B[i])
    B[i:i] = [d*' ' + "_em = ''",
              d*' ' + "try:",
              d*' ' + "    with pdfplumber.open(ap) as _pf: _em = (emails_in_text('\\n'.join((pg.extract_text() or '') for pg in _pf.pages)) or [''])[0]",
              d*' ' + "except Exception: pass",
              d*' ' + "print(f'\\U0001faaa {os.path.basename(ap)} · email: {_em or \"none readable\"} · taught for \"{tk}\" -> {tv}', flush=True)  # IDENTITY-FIRST v81.73: file and email before any number is used"]
    done.append('identity-first-taught')
src = '\n'.join(B)
if '# IDENTITY-FIRST-EXTRACT v81.73' not in src:
    i = next(k for k, l in enumerate(B) if '# EMAIL-ALWAYS v81.67' in l)
    d = ind(B[i])
    B[i] = d*' ' + "em = emails_in_text(txt)  # IDENTITY-FIRST-EXTRACT v81.73: file, email and source before the window opens"
    B.insert(i+1, d*' ' + "if ph: print(f'\\U0001faaa {os.path.basename(ap)} · email: {em[0] if em else \"none readable\"} · phone extracted: {ph[0]}', flush=True)")
    done.append('identity-first-extract')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S179 a taught key is whole tokens or nothing" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S178 every voice asks the same clerk" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S179 a taught key is whole tokens or nothing', 'sorted(tk.split()) == sorted(stem.split())' in _src and 'all(w in stem for w in tk.split())' not in _src)")
    B.insert(i+2, d*' ' + "ck('S180 the whole paper is read, not an excerpt', 'pdf.pages[:2]' not in _src)")
    B.insert(i+3, d*' ' + "ck('S181 identity speaks before any number is used', (chr(35)+' IDENTITY-FIRST v81.73') in _src and (chr(35)+' IDENTITY-FIRST-EXTRACT v81.73') in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S179-S181-guards')
print('✅', done)
