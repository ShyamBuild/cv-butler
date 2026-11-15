import ast, os
done = []
F = open('briefing.py').read()
oldw = '    where = f"Company: {cli}" + (f" | Location: {loc}" if loc else "")'
if oldw in F and 'where=at' not in F:
    F = F.replace(oldw, oldw + '\n    at = cli + (f", {loc}" if loc else "")', 1)
    F = F.replace("return tpl.format(name=name, position=title, company=cli, location=loc or '-', where_line=where)",
                  "return tpl.format(name=name, position=title, company=cli, location=loc or '-', where_line=where, where=at)", 1)
    done.append('fmt-tpl-where')
if 'DEFAULT_TPL = (' in F and "couldn't reach you." not in F:
    i = F.index('DEFAULT_TPL = (')
    j = F.index('Thanks!")', i) + len('Thanks!")')
    F = F[:i] + ('DEFAULT_TPL = ("Hi {name}, Sundeep Rana here from Sunsoft Technology. 📞\\n"\n'
                 '"I tried calling you today regarding the {position} role at {where}, but couldn\'t reach you.\\n"\n'
                 '"Kindly share your updated CV in PDF format here, along with a good time to reconnect. 🙏\\n"\n'
                 '"Regards,\\nSundeep Rana")') + F[j:]
    done.append('default-tpl-voice')
if 'def do_missed(arg, root, say=print, ask=None):' in F:
    F = F.replace('def do_missed(arg, root, say=print, ask=None):',
                  'def do_missed(arg, root, say=print, ask=None, words=None):', 1)
    F = F.replace("_tpl_for(['missed'])", "_tpl_for(words or ['missed'])")
    done.append('missed-words-param')
for a, b in [("elif cmd == 'nudge': do_missed(arg, root, print)",
              "elif cmd == 'nudge': do_missed(arg, root, print, words=['awaiting', 'confirmation'])"),
             ("do_missed(q[len(\"nudge\"):].strip(), root)",
              "do_missed(q[len(\"nudge\"):].strip(), root, words=['awaiting', 'confirmation'])")]:
    if a in F:
        F = F.replace(a, b, 1); done.append('nudge-awaiting-voice')
open('briefing.py', 'w').write(F); ast.parse(F)
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if l.strip().startswith("ck('S53 professional template live'") and "'{where}' in _tpl" not in l:
        d = len(l) - len(l.lstrip())
        B[k] = d*' ' + "ck('S53 professional template live', 'Sundeep Rana' in _tpl and ('{where}' in _tpl or '{where_line}' in _tpl) and 'where=at' in _br)"
        done.append('S53-evolved'); break
if "'S57 unified voice + emojis" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S56 log trim + single helper defs" in l)
    d = len(B[i]) - len(B[i].lstrip())
    B.insert(i+1, d*' ' + "_tm = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'missed.txt')).read() if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'missed.txt')) else ''")
    B.insert(i+2, d*' ' + "ck('S57 unified voice + emojis', 'Regards,' in _tm and '📞' in _tm and 'where=at' in _br)")
    done.append('S57-guard')
if "'S58 nudge speaks awaiting voice" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S57 unified voice + emojis" in l)
    d = len(B[i]) - len(B[i].lstrip())
    B.insert(i+1, d*' ' + "ck('S58 nudge speaks awaiting voice', \"words=['awaiting', 'confirmation']\" in _br and 'def do_missed(arg, root, say=print, ask=None, words=None)' in _br)")
    done.append('S58-guard')
open('butler.py', 'w').write('\n'.join(B))
print('✅', done)
