import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
out = []
for l in B:
    if l.strip().startswith('print(') and '\\U0001f4e7' in l:
        done.append('email-dup-removed'); continue
    out.append(l)
B = out
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
W = os.path.join(os.getcwd(), 'wa.py')
w = open(W).read().split('\n')
out = []
for l in w:
    if 'message is in the WhatsApp text field - review it in the opened window, then:' in l:
        done.append('review-line-removed'); continue
    out.append(l)
w = out
for k, l in enumerate(w):
    if 'opening WhatsApp Web in the BUTLER window' in l:
        w.insert(k+1, ind(l)*' ' + "_notwa = False  # CONCISE v81.91: the paste advice is wrong when WhatsApp has already said there is no field")
        done.append('notwa-init'); break
for k, l in enumerate(w):
    if "isn't on WhatsApp - there is no message field to paste into" in l:
        w.insert(k+1, ind(l)*' ' + "        _notwa = True")
        done.append('notwa-set'); break
for k, l in enumerate(w):
    if l.strip().startswith("say('⚠️ field did not take the text automatically"):
        w[k] = ind(l)*' ' + "if not _notwa: " + l.strip()
        done.append('advice-conditional'); break
srcw = '\n'.join(w); ast.parse(srcw); open(W, 'w').write(srcw)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S195 identity speaks once, not twice", "'S194 every number carries its page and its section", "ck('S195 identity speaks once, not twice', ('\\U0001f4'+'e7') not in _src and open(os.path.join(BASE_DIR, 'wa.py')).read().count('message is in the WhatsApp text field') == 1)"),
      ("'S196 no paste advice when WhatsApp says no field", "'S195 identity speaks once, not twice", "ck('S196 no paste advice when WhatsApp says no field', 'if not _notwa: ' in open(os.path.join(BASE_DIR, 'wa.py')).read() and (chr(35)+' CONCISE v81.91') in open(os.path.join(BASE_DIR, 'wa.py')).read())")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S193 a number absent from WhatsApp is named aloud")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
