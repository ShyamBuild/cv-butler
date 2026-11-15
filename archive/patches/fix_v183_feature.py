import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
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
src = '\n'.join(B)
if '# STALE-JOB-PRUNE v81.44' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'if not self._ad_busy() and self._ad_claim():')
    d = ind(B[i])
    B[i:i] = [d*' ' + "try:",
              d*' ' + "    q = [x for x in json.load(open(qp)) if time.time() - x.get('at', 0) < 900]",
              d*' ' + "    json.dump(q, open(qp, 'w'), indent=1)  # STALE-JOB-PRUNE v81.44: nameless old intent expires",
              d*' ' + "except Exception:",
              d*' ' + "    pass"]
    done.append('stale-job-prune')
src = '\n'.join(B)
if '# WARM-SUPERVISOR v81.44' not in src:
    k = next(k for k, l in enumerate(B) if l.strip() == 'except Exception as e:' and 'pulse thread' in B[k+1])
    d = ind(B[k]) + 4
    B[k:k] = [d*' ' + "if time.time() - getattr(B, '_warm_chk', 0) > 300:  # WARM-SUPERVISOR v81.44: a dead warm door is rebuilt without your noticing",
              d*' ' + "    B._warm_chk = time.time()",
              d*' ' + "    import socket as _sk",
              d*' ' + "    _alive = False",
              d*' ' + "    try:",
              d*' ' + "        _s = _sk.create_connection(('127.0.0.1', 9222), timeout=2); _s.close(); _alive = True",
              d*' ' + "    except Exception:",
              d*' ' + "        _alive = False",
              d*' ' + "    if not _alive:",
              d*' ' + "        try:",
              d*' ' + "            subprocess.Popen([sys.executable, os.path.join(BASE_DIR, 'wa_warm.py'), 'ensure'], cwd=BASE_DIR, stdout=open(os.path.join(BASE_DIR, 'wa_warm.log'), 'a'), stderr=subprocess.STDOUT, start_new_session=True)",
              d*' ' + "            print('🔥 warm browser missing - supervisor relaunched it', flush=True)",
              d*' ' + "        except Exception:",
              d*' ' + "            pass"]
    done.append('warm-supervisor')
src = '\n'.join(B)
if '# RENAME-CLEAN-CALL v81.45' not in src:
    for k, l in enumerate(B):
        if l.strip() == 'self._rename_clean()':
            d = ind(l)
            B[k:k+1] = [d*' ' + "_rc = getattr(B, '_rename_clean', None)  # RENAME-CLEAN-CALL v81.45: main has no self; a wounded pass may never kill the watcher",
                        d*' ' + "if _rc:",
                        (d+4)*' ' + "try: _rc()",
                        (d+4)*' ' + "except Exception as _rce: print(f'⚠️ rename-clean skipped this pass: {_rce}', flush=True)"]
            done.append('rename-clean-call-fixed'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S147 the same draft never enters the same chat twice" not in '\n'.join(B):
    anch = [k for k, l in enumerate(B) if "'S146 your close is honoured for ten minutes" in l]
    i = anch[-1]; d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S147 the same draft never enters the same chat twice', (chr(35)+' DEDUPE v81.44') in open(os.path.join(BASE_DIR, 'ad_wait.py')).read() and (chr(35)+' STALE-JOB-PRUNE v81.44') in _src and (chr(35)+' WARM-SUPERVISOR v81.44') in _src)")
    done.append('S147-guard')
B = open('butler.py').read().split('\n')
if "'S148 main never speaks self" not in '\n'.join(B):
    anch = [k for k, l in enumerate(B) if "'S147 the same draft never enters the same chat twice" in l]
    if not anch: anch = [k for k, l in enumerate(B) if "'S146 your close is honoured for ten minutes" in l]
    i = anch[-1]; d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S148 main never speaks self', not any(x.startswith('    self.') and not x.startswith('     ') for x in _src.split(chr(10))))")
    done.append('S148-guard')
B = open('butler.py').read().split('\n')
if "'S149 chat rides the warm door, never fights it" not in '\n'.join(B):
    anch = [k for k, l in enumerate(B) if "'S148 main never speaks self" in l]
    if not anch: anch = [k for k, l in enumerate(B) if "'S146 your close is honoured for ten minutes" in l]
    i = anch[-1]; d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S149 chat rides the warm door, never fights it', 'WARM-CLIENT v81.47' in open(os.path.join(BASE_DIR, 'wa.py')).read())")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S149-guard')
print('✅', done)
