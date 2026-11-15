import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
F = open('briefing.py').read().split('\n')
i = next(k for k, l in enumerate(F) if 'q = input("you> ").strip()' in l)
if F[i+1].strip() == 'except EOFError:' and F[i+2].strip() == 'break' and 'except KeyboardInterrupt:' not in F[i+1:i+5]:
    F[i+3:i+3] = [ind(F[i+1])*' ' + 'except KeyboardInterrupt:',
                  ind(F[i+1])*' ' + '    print("\\n👋 chat closed - watchers keep running (focus clear stops them)")',
                  ind(F[i+1])*' ' + '    break']
    done.append('chat-ctrl-c-graceful')
new = '\n'.join(F); ast.parse(new); open('briefing.py', 'w').write(new)
B = open('butler.py').read().split('\n')
if "'S65 chat ctrl-c graceful" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S64 referral voice not shadowed" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S65 chat ctrl-c graceful', 'except KeyboardInterrupt:' in _br.split('q = input(\"you> \")')[1][:300])")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S65-guard')
print('✅', done)
