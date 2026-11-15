import ast
p = 'butler.py'; L = open(p).read().split('\n'); done = []
for i, l in enumerate(L):
    if l.strip().startswith('RULES_VERSION ='):
        if 'v19-fresh-eyes' not in l:
            d = len(l) - len(l.lstrip())
            L[i] = d*' ' + "RULES_VERSION = 'v19-fresh-eyes'"
            done.append('rules-bumped-indent-safe')
        break
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
Ls = open('ship.sh').read().split('\n')
for i, l in enumerate(Ls):
    if 'git status --porcelain' in l and 'uncommitted' in l and '-- butler.py' not in l:
        Ls[i] = '  if [ -n "$(git status --porcelain -- butler.py briefing.py wa.py cleaner.py ship.sh PROTOCOL.md butler_check.py requirements.txt)" ]; then echo "⚠️ uncommitted CODE edits - gate them: ./ship.sh \\"msg\\""; else echo "📚 code clean & in sync (runtime/data ignored)"; fi'
        done.append('health-scoped')
        break
open('ship.sh', 'w').write('\n'.join(Ls))
print('✅', done or 'nothing missing')
