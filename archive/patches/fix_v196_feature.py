import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if l.strip().startswith("PHONE_RE = re.compile("):
        B[k] = ind(l)*' ' + "PHONE_RE = re.compile(r'(?:\\+?91[ \\-\\.]?)?(?<!\\d)([6-9](?:[ \\-\\.]?\\d){9})(?!\\d)')  # PINCODE-SAFE v81.58: separators never cross a newline; digits bounded both sides"
        done.append('pincode-safe-regex'); break
for k, l in enumerate(B):
    if 'st.st_ino}|{st.st_mtime}|{st.st_size}' in l and 'v2|' not in l:
        B[k] = ind(l)*' ' + 'st = os.stat(p); k = f"v2|{st.st_ino}|{st.st_mtime}|{st.st_size}"  # CACHE-SALT v81.58: a cured extractor never trusts the poisoned cache'
        done.append('cache-salt'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S168 pincodes never lend digits to phones" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S167 the shared door is never queried like an owned one" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S168 pincodes never lend digits to phones', phones_in_text('Chennai, India 600050\\n9597850419\\n') == ['9597850419'] and phones_in_text('600050\\n9597850419') == ['9597850419'])")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S168-guard')
print('✅', done)
