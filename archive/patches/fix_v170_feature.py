import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
AW = os.path.join(os.getcwd(), 'ad_wait.py')
s = open(AW).read()
if "'pid': os.getpid()" not in s:
    inline = "{'state': s, 'ts': time.time(), 'phone': phone, 'who': who}"
    old2 = "st = {'state': s, 'ts': time.time(), 'phone': phone, 'who': who}"
    if inline in s:
        s = s.replace(inline, "{'state': s, 'ts': time.time(), 'phone': phone, 'who': who, 'pid': os.getpid()}")
        s = s.replace('# AD-WAIT v81.33:', '# AD-WAIT v81.36:', 1)
        open(AW, 'w').write(s); done.append('ad-wait-pid')
    elif old2 in s:
        s = s.replace(old2, old2[:-1] + ", 'pid': os.getpid()}")
        open(AW, 'w').write(s); done.append('ad-wait-pid')
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if l.strip() == "if st.get('state') == 'waiting': return time.time() - st.get('ts', 0) < 1900":
        d = ind(l)
        B[k:k+1] = [d*' ' + "if getattr(self, '_ad_held', 0) > time.time(): return True  # HELD v81.35: one fire per tick, decided synchronously",
                    d*' ' + "if st.get('state') == 'waiting':  # PID-ALIVE v81.34: a killed watcher is not a busy window",
                    (d+4)*' ' + "try: os.kill(int(st.get('pid', 0)), 0)",
                    (d+4)*' ' + "except Exception: return False",
                    (d+4)*' ' + "return time.time() - st.get('ts', 0) < 1900"]
        done.append('busy-pid-alive-held'); break
src = '\n'.join(B)
if '# SWEEP-RESET v81.34' not in src:
    i = next(k for k, l in enumerate(B) if '# STALE-WINDOW-SWEEP v81.32' in l)
    d = ind(B[i])
    B[i+1:i+1] = [d*' ' + "try:",
                  d*' ' + "    json.dump({'state': 'retired', 'ts': time.time()}, open(os.path.join(BASE_DIR, 'ad_state.json'), 'w'))  # SWEEP-RESET v81.34",
                  d*' ' + "except Exception:",
                  d*' ' + "    pass"]
    done.append('sweep-reset')
src = '\n'.join(B)
if '# SINGLE-FLIGHT v81.35' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def _ad_busy(self):'))
    d = ind(B[i])
    B[i:i] = [d*' ' + "def _ad_claim(self):  # SINGLE-FLIGHT v81.35: one release per state change; two tick callers, one queue",
              d*' ' + "    now = time.time()",
              d*' ' + "    if now - getattr(self, '_ad_last_release', 0) < 8: return False",
              d*' ' + "    self._ad_last_release = now",
              d*' ' + "    return True",
              ""]
    for k, l in enumerate(B):
        if l.strip() == 'if not self._ad_busy():':
            B[k] = ind(l)*' ' + 'if not self._ad_busy() and self._ad_claim():'
            break
    done.append('single-flight')
src = '\n'.join(B)
if 'self._ad_held = time.time() + 90' not in src:
    i = next(k for k, l in enumerate(B) if 'ad_wait.py' in l and 'Popen' in l)
    d = ind(B[i])
    B.insert(i, d*' ' + "self._ad_held = time.time() + 90  # HELD v81.35: mark the window held before the child can speak")
    done.append('held-at-fire')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S138 a dead watcher never blocks the queue" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S137 no ownerless windows survive a relaunch" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S138 a dead watcher never blocks the queue', (chr(35)+' PID-ALIVE v81.34') in _src and (chr(35)+' SWEEP-RESET v81.34') in _src and 'os.getpid()' in open(os.path.join(BASE_DIR, 'ad_wait.py')).read())")
    B.insert(i+2, d*' ' + "ck('S139 one fire per tick, no profile races', (chr(35)+' HELD v81.35') in _src and ('self._ad_held = time.time() ' + '+ 90') in _src)")
    B.insert(i+3, d*' ' + "ck('S140 one release per state change', (chr(35)+' SINGLE-FLIGHT v81.35') in _src and ('def _ad_' + 'claim') in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S138-S140-guards')
print('✅', done)
