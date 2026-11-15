import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
D = os.getcwd()
open(os.path.join(D, 'ad_wait.py'), 'w').write('''# AD-WAIT v81.26: the window waits for your thumb; your close is an answer, not an accident
import os, re, sys, time
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import wa
from playwright.sync_api import sync_playwright
phone, tf = sys.argv[1], sys.argv[2]
who = sys.argv[3] if len(sys.argv) > 3 else ''
txt = open(tf, encoding='utf-8').read()
digits = re.sub(r'\\D', '', str(phone))
if len(digits) == 10: digits = '91' + digits
def state(s):
    try:
        import json as _j
        _j.dump({'state': s, 'ts': time.time(), 'phone': digits, 'who': who}, open(os.path.join(BASE, 'ad_state.json'), 'w'))
    except Exception:
        pass
print(f'\\U0001f310 opening WhatsApp Web in the BUTLER window for +{digits} ({who})\\u2026', flush=True)
state('waiting')
pw = sync_playwright().start()
browser = None
sent = False; closed = False
try:
    browser = pw.chromium.launch_persistent_context(os.path.join(BASE, 'wa_profile'), headless=False, no_viewport=True)
    page = browser.pages[0] if browser.pages else browser.new_page()
    if not wa._goto(page, f'https://web.whatsapp.com/send?phone={digits}', print):
        print('\\u26a0\\ufe0f chat page did not load - scan QR in the opened window if asked, then retry', flush=True)
    else:
        try:
            if "isn't on WhatsApp" in (page.content() or ''):
                print('\\u26a0\\ufe0f number not registered - nothing drafted', flush=True)
                raise SystemExit(0)
        except SystemExit:
            raise
        except Exception:
            pass
        ok = wa._place_text(page, txt, print)
        if not ok:
            print('\\u26a0\\ufe0f field did not take the text on first try - will retry while waiting', flush=True)
        print('\\U0001f4dd draft in field - window STAYS open until you send or close (30 min idle max)', flush=True)
        placed = time.time(); deadline = placed + 1800; empties = 0; seen_alive = False; retried = False
        while time.time() < deadline:
            time.sleep(3)
            alive = False; cur = ''
            for sel in wa.COMPOSE_SELS:
                try:
                    v = page.eval_on_selector(sel, "e => e.innerText || e.textContent || ''")
                    alive = True
                    if v: cur = v; break
                except Exception:
                    continue
            if not alive:
                if seen_alive and time.time() - placed > 15:
                    closed = True
                    print('\\U0001f44b window closed by you - this tag\\'s task is DONE for this cycle; queued twins for this candidate dropped', flush=True)
                    break
                if time.time() - placed > 120:
                    print('\\u26a0\\ufe0f compose box never appeared; retiring', flush=True); break
                continue
            seen_alive = True
            if not cur.strip():
                if not ok and not retried and time.time() - placed > 5:
                    retried = True
                    ok = wa._place_text(page, txt, print)
                    continue
                if time.time() - placed > 10:
                    empties += 1
                    if empties >= 2:
                        sent = True
                        print('\\u2705 field empty - sent by your hand; arming follow-up clock', flush=True)
                        try: wa._arm(digits, txt)
                        except Exception: pass
                        break
                else:
                    empties = 0
            else:
                empties = 0
except SystemExit:
    pass
except Exception as e:
    print(f'\\u26a0\\ufe0f wa-wait failed: {e}', flush=True)
finally:
    state('sent' if sent else ('closed' if closed else 'retired'))
    try:
        if browser is not None: browser.close()
    except Exception:
        pass
    try: pw.stop()
    except Exception: pass
print('\\U0001f44b wa-wait retired', flush=True)
''')
done.append('ad-wait-v81.26')
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if l.strip().startswith("subprocess.Popen([sys.executable, os.path.join(BASE_DIR, 'ad_wait.py')"):
        B[k] = ind(l)*' ' + "subprocess.Popen([sys.executable, os.path.join(BASE_DIR, 'ad_wait.py'), d, tf, nm], cwd=BASE_DIR, stdout=lf, stderr=subprocess.STDOUT)  # WA-WAIT v81.26: window lives until send or close; close means done"
        done.append('popen-who'); break
src = '\n'.join(B)
if '# CLOSE-MEANS-DONE v81.26' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def _ad_busy(self):'))
    d = ind(B[i])
    B[i:i] = [d*' ' + "def _ad_prune_q(self):  # CLOSE-MEANS-DONE v81.26: stale intent expires; your close finishes the cycle",
              d*' ' + "    try: q = json.load(open(os.path.join(BASE_DIR, 'autodraft_queue.json')))",
              d*' ' + "    except Exception: return",
              d*' ' + "    try: st = json.load(open(os.path.join(BASE_DIR, 'ad_state.json')))",
              d*' ' + "    except Exception: st = {}",
              d*' ' + "    now = time.time(); keep = []",
              d*' ' + "    for x in q:",
              d*' ' + "        age = now - x.get('at', now)",
              d*' ' + "        if age > 900:",
              d*' ' + "            print(f\"🗑 dropped stale queued draft (age {int(age)}s) for +{x.get('phone')} - re-tag to fire fresh\", flush=True); continue",
              d*' ' + "        if st.get('state') in ('closed', 'sent') and st.get('ts', 0) > x.get('at', 0):",
              d*' ' + "            sd = re.sub(r'\\D', '', str(st.get('phone', '')))[-10:]; xd = re.sub(r'\\D', '', str(x.get('phone', '')))[-10:]",
              d*' ' + "            if (sd and sd == xd) or (st.get('who') and st.get('who') == x.get('who')):",
              d*' ' + "                print(f\"🗑 dropped queued twin for +{x.get('phone')} ({x.get('who')}) - you closed or sent its window; this cycle is done\", flush=True); continue",
              d*' ' + "        keep.append(x)",
              d*' ' + "    if len(keep) != len(q):",
              d*' ' + "        json.dump(keep, open(os.path.join(BASE_DIR, 'autodraft_queue.json'), 'w'), indent=1)",
              ""]
    done.append('prune-q')
    for k, l in enumerate(B):
        if l.strip() == 'if not self._ad_busy():':
            B[k] = ind(l)*' ' + 'self._ad_prune_q()'
            B.insert(k+1, l)
            break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S130 close means done and stale queues drop" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S129 ad_wait knows load-silence from closed windows" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S130 close means done and stale queues drop', (chr(35)+' CLOSE-MEANS-DONE') in _src and '_ad_prune_q' in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S130-guard')
print('✅', done)
