import ast
p = 'wa.py'; L = open(p).read().split('\n'); done = []
for k, l in enumerate(L):
    if '[Enter] I clicked send myself' in l and 'keep waiting' not in l:
        d = len(l) - len(l.lstrip())
        L[k:k+1] = [d*' ' + 'say("📝 message is in the WhatsApp text field - the window STAYS open until you choose:")',
                    d*' ' + 'while True:',
                    d*' ' + '    c = (ask or input)("   [s] I clicked send myself · [x] discard & clear · [q] leave in field & close · [Enter] keep waiting: ").strip().lower()',
                    d*' ' + "    if c == '':",
                    d*' ' + '        say("   …still open - take your time (s / x / q)")',
                    d*' ' + '        continue',
                    d*' ' + '    break']
        done.append('enter-keeps-window')
        break
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done or 'nothing missing')
