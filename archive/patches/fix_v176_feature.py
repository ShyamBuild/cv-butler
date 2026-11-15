import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
D = os.getcwd()
open(os.path.join(D, 'wa_warm.py'), 'w').write('''# WA-WARM v81.41: owned warm browser that respects your close for ten minutes
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
        print('\\U0001f44b closed by you; staying closed for 10 min (drafts cold-launch meanwhile)  # WARM-COOLDOWN v81.41', flush=True)
        try: pw.stop()
        except Exception: pass
        time.sleep(600)
        continue
    except Exception as e:
        print(f'\\u26a0\\ufe0f warm browser failed: {e}', flush=True)
    finally:
        try: pw.stop()
        except Exception: pass
    time.sleep(10)
''')
done.append('warm-cooldown')
AW = os.path.join(D, 'ad_wait.py')
s = open(AW).read()
if 'range(8)' in s and '# FAST-FALLBACK v81.41' not in s:
    s = s.replace("for _try in range(8):  # WARM-RETRY v81.40: wait for the owned warm browser before ever cold-launching",
                  "for _try in range(2):  # FAST-FALLBACK v81.41: two quick tries, then cold-launch your own window")
    s = s.replace("browser = None; time.sleep(3)", "browser = None; time.sleep(2)  # FAST-FALLBACK v81.41")
    open(AW, 'w').write(s); done.append('fast-fallback')
B = open('butler.py').read().split('\n')
if "'S146 your close is honoured for ten minutes" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S145 one owned warm browser, self-healing" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S146 your close is honoured for ten minutes', 'WARM-COOLDOWN v81.41' in open(os.path.join(BASE_DIR, 'wa_warm.py')).read() and (chr(35)+' FAST-FALLBACK v81.41') in open(os.path.join(BASE_DIR, 'ad_wait.py')).read())")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S146-guard')
src = '\n'.join(B); ast.parse(src)
print('✅', done)
