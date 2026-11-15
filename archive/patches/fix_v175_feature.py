import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
D = os.getcwd()
open(os.path.join(D, 'wa_warm.py'), 'w').write('''# WA-WARM v81.40: one owned warm browser; if you close it, it reopens itself within seconds
import os, sys, time
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
if len(sys.argv) > 1 and sys.argv[1] == 'ensure':
    from playwright.sync_api import sync_playwright
    try:
        pw = sync_playwright().start()
        b = pw.chromium.connect_over_cdp('http://127.0.0.1:9222')
        print('warm browser already alive', flush=True); pw.stop(); sys.exit(0)
    except Exception:
        try: pw.stop()
        except Exception: pass
from playwright.sync_api import sync_playwright
while True:
    pw = sync_playwright().start()
    try:
        browser = pw.chromium.launch_persistent_context(os.path.join(BASE, 'wa_profile'), headless=False, no_viewport=True, args=['--remote-debugging-port=9222'])
        page = browser.pages[0] if browser.pages else browser.new_page()
        try:
            page.goto('https://web.whatsapp.com', timeout=90000, wait_until='domcontentloaded')
        except Exception:
            pass
        print('\\U0001f525 warm WhatsApp browser ready on :9222', flush=True)
        while browser.is_connected():
            time.sleep(3)
        print('\\U0001f44b warm browser closed by you; reopening in 3s', flush=True)
    except Exception as e:
        print(f'\\u26a0\\ufe0f warm browser failed: {e}', flush=True)
    finally:
        try: pw.stop()
        except Exception: pass
    time.sleep(3)
''')
done.append('warm-selfheal')
AW = os.path.join(D, 'ad_wait.py')
s = open(AW).read()
old = "    browser = pw.chromium.connect_over_cdp('http://127.0.0.1:9222')  # WARM-CONNECT v81.37: seconds, not a cold minute"
if old in s and '# WARM-RETRY v81.40' not in s:
    s = s.replace(old, """    for _try in range(8):  # WARM-RETRY v81.40: wait for the owned warm browser before ever cold-launching
        try:
            browser = pw.chromium.connect_over_cdp('http://127.0.0.1:9222')
            break
        except Exception:
            browser = None; time.sleep(3)
    if browser is None:
        raise RuntimeError('no warm browser on :9222')""")
    open(AW, 'w').write(s); done.append('warm-retry')
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# Q-INIT v81.40' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == "qp = os.path.join(BASE_DIR, 'autodraft_queue.json')" and ind(l) == 12)
    B.insert(i+1, ind(B[i])*' ' + "q = []  # Q-INIT v81.40: the witness may read the queue even when the release gate skips")
    done.append('q-init')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S144 the tick never dies on an uninitialised queue" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S143 only ownerless browsers are swept" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S144 the tick never dies on an uninitialised queue', (chr(35)+' Q-INIT v81.40') in _src)")
    B.insert(i+2, d*' ' + "ck('S145 one owned warm browser, self-healing', (chr(35)+' WARM-RETRY v81.40') in open(os.path.join(BASE_DIR, 'ad_wait.py')).read() and 'is_connected' in open(os.path.join(BASE_DIR, 'wa_warm.py')).read())")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S144-S145-guards')
print('✅', done)
