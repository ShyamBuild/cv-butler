import ast
p = 'butler.py'; L = open(p).read().split('\n'); done = []
i = next(k for k, l in enumerate(L) if l.strip().startswith('def position_folder_for('))
d = len(L[i]) - len(L[i].lstrip())
j = i + 1
while j < len(L) and (not L[j].strip() or (len(L[j]) - len(L[j].lstrip())) > d): j += 1
L[i:j] = [d*' ' + 'def position_folder_for(self, p):',
          d*' ' + '    dd = os.path.dirname(os.path.abspath(p))',
          d*' ' + '    rel = os.path.relpath(dd, self.root)',
          d*' ' + "    parts = [] if rel == '.' else rel.split(os.sep)",
          d*' ' + '    if len(parts) >= 2:',
          d*' ' + '        return os.path.join(self.root, parts[0], parts[1])',
          d*' ' + '    return dd',
          '']
done.append('position-folder-depth2')
if "'S18 no tag folders at company root'" not in '\n'.join(L):
    k = next(x for x, l in enumerate(L) if "'S17 playwright import" in l)
    dd = len(L[k]) - len(L[k].lstrip())
    L[k+1:k+1] = [dd*' ' + "_tags = ['Awaiting CV Update','Awaiting JD Confirmation','Call Scheduled','Feedback Pending','Interview Scheduled','Closed – Not Proceeding','Ready for Manager Review','Rejected by Client']",
                  dd*' ' + "    _tg = {t.lower().replace('\\u2013','-').replace(' ','_') for t in _tags}",
                  dd*' ' + "    ck('S18 no tag folders at company root', not any(os.path.isdir(os.path.join(root, c)) and c.lower().replace('\\u2013','-').replace(' ','_') in _tg for c in os.listdir(root)))"]
    done.append('S18-guard')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done or 'nothing missing')
