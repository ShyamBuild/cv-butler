import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# PULSE-THREAD v81.13' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'ex = ThreadPoolExecutor(max_workers=4)')
    d = ind(B[i])
    B[i+1:i+1] = [d*' ' + "def _pulse_loop():  # PULSE-THREAD v81.13: the pulse lives in no branch's custody",
                  d*' ' + "    while True:",
                  d*' ' + "        try:",
                  d*' ' + "            if _t.time() - getattr(B, '_last_poll', 0) > 4:",
                  d*' ' + "                B._last_poll = _t.time()",
                  d*' ' + "                for _cp in B._tag_poll(): ex.submit(work, _cp)",
                  d*' ' + "                B._autodraft_tick()",
                  d*' ' + "            if _t.time() - getattr(B, '_last_hb_t', 0) > 120:",
                  d*' ' + "                B._last_hb_t = _t.time()",
                  d*' ' + "                try: B._heal(print)",
                  d*' ' + "                except Exception: pass",
                  d*' ' + "            if _t.time() - getattr(B, '_last_snap_t', 0) > 3600:",
                  d*' ' + "                B._last_snap_t = _t.time()",
                  d*' ' + "                try: B._snapshot(print)",
                  d*' ' + "                except Exception: pass",
                  d*' ' + "        except Exception as e:",
                  d*' ' + "            print(f'⚠️ pulse thread: {e}', flush=True)",
                  d*' ' + "        _t.sleep(2)",
                  d*' ' + "import threading as _th",
                  d*' ' + "_th.Thread(target=_pulse_loop, daemon=True).start()",
                  ""]
    done.append('pulse-thread')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S120 the pulse owns its own thread" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S119 the REPL door keys on INTERACTIVE" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S120 the pulse owns its own thread', (chr(35)+' PULSE-THREAD') in _src and 'Thread(target=_pulse_loop' in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S120-guard')
print('✅', done)
