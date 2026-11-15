import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
os.makedirs('templates', exist_ok=True)
REF = ("Hi {name}, Sundeep Rana here from Sunsoft Technology. 🙏\n"
       "Thank you for your time regarding the {position} role at {where}.\n"
       "If any colleague or friend may fit, kindly share their contact - or ask them to WhatsApp me a PDF CV, or call me directly.\n"
       "I will keep you in mind for future matches. ✨\n"
       "Regards,\n"
       "Sundeep Rana")
if not os.path.exists('templates/referral.txt'):
    open('templates/referral.txt', 'w').write(REF + '\n'); done.append('referral-template')
F = open('briefing.py').read().split('\n')
for k, l in enumerate(F):
    if l.strip() == "if 'rejected' in st or 'closed' in st: return ['rejected']":
        F[k:k+1] = [ind(l)*' ' + "if 'closed' in st: return ['referral']",
                    ind(l)*' ' + "if 'rejected' in st: return ['rejected']"]
        done.append('stage-closed-referral'); break
for k, l in enumerate(F):
    if "'follow','tpltest')" in l and "'refer'" not in l:
        F[k] = l.replace("'tpltest')", "'tpltest','refer')"); done.append('door-list'); break
for k, l in enumerate(F):
    if l.strip().startswith("elif cmd == 'tpltest'"):
        F.insert(k+1, ind(l)*' ' + "elif cmd == 'refer': do_send(arg, root, ['referral'], print)")
        done.append('cli-refer'); break
for k, l in enumerate(F):
    if l.strip().startswith("if q.lower().startswith('tpltest ')"):
        F.insert(k+1, ind(l)*' ' + "if q.lower().startswith('refer '): do_send(q[6:].strip(), root, ['referral']); continue")
        done.append('chat-refer'); break
new = '\n'.join(F); ast.parse(new); open('briefing.py', 'w').write(new)
C = open('cadence.py').read()
oldc = "if (st.startswith('rejected') or st.startswith('closed')) and not any("
if oldc in C:
    C = C.replace(oldc, "if st.startswith('rejected') and not any(", 1)
    open('cadence.py', 'w').write(C); done.append('cadence-closed-manual')
B = open('butler.py').read().split('\n')
if "'S63 referral voice for closed candidates" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S62 tpltest + split hardening" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S63 referral voice for closed candidates', os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'referral.txt')) and \"cmd == 'refer'\" in _br and \"'closed' in st: return ['referral']\" in _br)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S63-guard')
print('✅', done)
