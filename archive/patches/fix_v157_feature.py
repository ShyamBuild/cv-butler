import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
D = os.getcwd()
open(os.path.join(D, 'ad_wait.py'), 'w').write('''# AD-WAIT v81.25: the window waits for your thumb; page-load silence is not a closed window
import os, re, sys, time
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
                print('\\u26a0\\ufe0f number not registered - nothing drafted', flush=True)
                raise SystemExit(0)
        except SystemExit:
            raise
        except Exception:
            pass
        ok = wa._place_text(page, txt, print)
        if not ok:
            print('\\u26a0\\ufe0f field did not take the text on first try - will retry while waiting', flush=True)
        print('\\U0001f4dd draft in field - window STAYS open until you send (or 30 min idle)', flush=True)
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
                    print('\\U0001f44b window closed by you; retiring', flush=True); break
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
    state('sent' if sent else 'retired')
    try:
        if browser is not None: browser.close()
    except Exception:
        pass
    try: pw.stop()
    except Exception: pass
print('\\U0001f44b wa-wait retired', flush=True)
''')
done.append('ad-wait-v81.25')
B = open('butler.py').read().split('\n')
if "'S129 ad_wait knows load-silence from closed windows" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S128 the queue advances on your send" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S129 ad_wait knows load-silence from closed windows', 'AD-WAIT v81.25' in open(os.path.join(BASE_DIR, 'ad_wait.py')).read())")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S129-guard')
src = '\n'.join(B); ast.parse(src)
print('✅', done)
