import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
D = os.getcwd()
AW = os.path.join(D, 'ad_wait.py')
s = open(AW).read()
if '# WARM-RETRY v81.40' not in s:
    if 'for _try in range(8):' in s:
        s = s.replace("for _try in range(8):  # WARM-RETRY v81.40: wait for the owned warm browser before ever cold-launching",
                      "for _try in range(2):  # WARM-RETRY v81.40 + FAST-FALLBACK v81.41: two quick tries, then cold-launch your own window")
    elif 'for _try in range(2):' in s:
        s = s.replace("for _try in range(2):  # FAST-FALLBACK v81.41:",
                      "for _try in range(2):  # WARM-RETRY v81.40 + FAST-FALLBACK v81.41:")
    if 'browser = None; time.sleep(3)' in s:
        s = s.replace('browser = None; time.sleep(3)', 'browser = None; time.sleep(2)  # FAST-FALLBACK v81.41')
    open(AW, 'w').write(s); done.append('marker-inherited')
B = open('butler.py').read().split('\n')
if "'S146 your close is honoured for ten minutes" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S145 one owned warm browser, self-healing" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S146 your close is honoured for ten minutes', 'WARM-COOLDOWN v81.41' in open(os.path.join(BASE_DIR, 'wa_warm.py')).read() and (chr(35)+' FAST-FALLBACK v81.41') in open(os.path.join(BASE_DIR, 'ad_wait.py')).read())")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S146-guard')
src = '\n'.join(B); ast.parse(src)
print('✅', done)
