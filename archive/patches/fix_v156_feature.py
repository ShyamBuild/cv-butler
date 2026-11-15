import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
D = os.getcwd()
AW = os.path.join(D, 'ad_wait.py')
if not os.path.exists(AW):
    open(AW, 'w').write('''import os, re, sys, time
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import wa
from playwright.sync_api import sync_playwright
phone, tf = sys.argv[1], sys.argv[2]
txt = open(tf, encoding='utf-8').read()
digits = re.sub(r'\\D', '', str(phone))
if len(digits) == 10: digits = '91' + digits
def state(s):
    try:
        import json as _j
        _j.dump({'state': s, 'ts': time.time()}, open(os.path.join(BASE, 'ad_state.json'), 'w'))
    except Exception:
        pass
print(f'\\U0001f310 opening WhatsApp Web in the BUTLER window for +{digits}\\u2026', flush=True)
state('waiting')
pw = sync_playwright().start()
browser = None
sent = False
try:
    browser = pw.chromium.launch_persistent_context(os.path.join(BASE, 'wa_profile'), headless=False, no_viewport=True)
    page = browser.pages[0] if browser.pages else browser.new_page()
    if not wa._goto(page, f'https://web.whatsapp.com/send?phone={digits}', print):
        print('\\u26a0\\ufe0f chat page did not load - scan QR in the opened window if asked, then retry', flush=True)
    else:
        try:
            if "isn't on WhatsApp" in (page.content() or ''):
                print('\\u26a0\\ufe0f number not registered - nothing drafted', flush=True); browser.close(); browser = None; pw.stop(); sys.exit(0)
        except SystemExit:
            raise
        except Exception:
            pass
        ok = wa._place_text(page, txt, print)
        if not ok:
            print('\\u26a0\\ufe0f field did not take the text automatically - paste from ad_draft.txt yourself', flush=True)
        print('\\U0001f4dd draft in field - window STAYS open until you send (or 30 min idle)', flush=True)
        placed = time.time(); deadline = placed + 1800; empties = 0
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
                print('\\U0001f44b window closed by you; retiring', flush=True); break
            if not cur.strip():
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
except Exception as e:
    print(f'\\u26a0\\ufe0f wa-wait failed: {e}', flush=True)
finally:
    state('sent' if sent else 'retired')
    try:
        if browser is not None: browser.close()
    except Exception:
        pass
    try: pw.stop()
    except Exception: pass
print('\\U0001f44b wa-wait retired', flush=True)
''')
    done.append('ad-wait-script')
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# WA-WAIT v81.24' not in src:
    i = next(k for k, l in enumerate(B) if "subprocess.Popen([sys.executable, '-c', 'import wa, sys; wa.send_review" in l)
    d = ind(B[i])
    B[i] = d*' ' + "subprocess.Popen([sys.executable, os.path.join(BASE_DIR, 'ad_wait.py'), d, tf], cwd=BASE_DIR, stdout=lf, stderr=subprocess.STDOUT)  # WA-WAIT v81.24: the window lives until your send empties the field"
    done.append('wa-wait-popen')
src = '\n'.join(B)
if '# SEND-AWARE v81.24' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def _ad_fire(self, d, txt, v, nm, say):'))
    d = ind(B[i])
    B[i:i] = [d*' ' + "def _ad_busy(self):  # SEND-AWARE v81.24: the queue advances on your actual send",
              d*' ' + "    try: st = json.load(open(os.path.join(BASE_DIR, 'ad_state.json')))",
              d*' ' + "    except Exception: return getattr(self, '_ad_pending', 0) > time.time()",
              d*' ' + "    if st.get('state') == 'waiting': return time.time() - st.get('ts', 0) < 1900",
              d*' ' + "    return False",
              ""]
    done.append('send-aware-busy')
    for k, l in enumerate(B):
        if l.strip() == "if getattr(self, '_ad_pending', 0) > time.time():":
            B[k] = ind(l)*' ' + 'if self._ad_busy():'
        if l.strip() == "if getattr(self, '_ad_pending', 0) <= time.time():":
            B[k] = ind(l)*' ' + 'if not self._ad_busy():'
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S127 the window waits for your thumb" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S126 the poll sees trace-less tag edits" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S127 the window waits for your thumb', (chr(35)+' WA-WAIT v81.24') in _src and os.path.exists(os.path.join(BASE_DIR, 'ad_wait.py')))")
    B.insert(i+2, d*' ' + "ck('S128 the queue advances on your send', (chr(35)+' SEND-AWARE') in _src and 'ad_state.json' in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S127-S128-guards')
print('✅', done)
