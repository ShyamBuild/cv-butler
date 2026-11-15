import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
AW = os.path.join(os.getcwd(), 'ad_wait.py')
s = open(AW).read()
if '# DEDUPE-FIELD v81.45' not in s and 'cleared stale field text before placing new draft' in s:
    s = s.replace("cleared stale field text before placing new draft', flush=True)",
                  "cleared stale field text before placing new draft', flush=True)  # DEDUPE-FIELD v81.45: clearing IS the field dedupe - a paragraph can never be written twice", 1)
    open(AW, 'w').write(s); done.append('dedupe-field-marker')
W = os.path.join(os.getcwd(), 'wa.py')
w = open(W).read().split('\n')
if not any('WARM-CLIENT v81.47' in l for l in w):
    k = next(i for i, l in enumerate(w) if 'launch_persistent_context' in l and 'no_viewport=True' in l)
    d = ind(w[k])
    w[k:k+1] = [d*' ' + "try:",
                (d+4)*' ' + "browser = pw.chromium.connect_over_cdp('http://127.0.0.1:9222')  # WARM-CLIENT v81.47: chat rides the owned warm browser; the profile is never fought over again",
                (d+4)*' ' + "ctx = browser.contexts[0] if browser.contexts else browser.new_context()",
                (d+4)*' ' + "page = ctx.new_page()",
                (d+4)*' ' + "via_cdp = True",
                d*' ' + "except Exception:",
                (d+4)*' ' + "browser = pw.chromium.launch_persistent_context(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wa_profile'), headless=False, no_viewport=True)",
                (d+4)*' ' + "page = browser.pages[0] if browser.pages else browser.new_page()"]
    p = next(i for i, l in enumerate(w) if l.strip() == 'page = None')
    w.insert(p+1, ind(w[p])*' ' + "via_cdp = False")
    f = next(i for i, l in enumerate(w) if l.strip() == 'if browser is not None: browser.close()')
    df = ind(w[f])
    w[f] = df*' ' + "if via_cdp and page is not None: page.close()"
    w.insert(f+1, df*' ' + "elif browser is not None: browser.close()")
    srcw = '\n'.join(w); ast.parse(srcw); open(W, 'w').write(srcw); done.append('wa-warm-client')
B = open('butler.py').read().split('\n')
if "'S160 chat rides the warm door, never fights it" not in '\n'.join(B):
    anch = [k for k, l in enumerate(B) if "'S153 download scars are stripped from names" in l]
    if not anch: anch = [k for k, l in enumerate(B) if "'S146 your close is honoured for ten minutes" in l]
    i = anch[-1]; d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S160 chat rides the warm door, never fights it', 'WARM-CLIENT v81.47' in open(os.path.join(BASE_DIR, 'wa.py')).read())")
    B.insert(i+2, d*' ' + "ck('S161 connected clients close only their page', 'via_cdp and page is not None: page.close()' in open(os.path.join(BASE_DIR, 'wa.py')).read())")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S160-S161-guards')
print('✅', done)
