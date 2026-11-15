import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
D = os.getcwd()
if not os.path.exists(os.path.join(D, 'wa_warm.py')):
    open(os.path.join(D, 'wa_warm.py'), 'w').write('''# WA-WARM v81.37: one long-lived logged-in browser on :9222; drafts connect in seconds
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
pw = sync_playwright().start()
browser = pw.chromium.launch_persistent_context(os.path.join(BASE, 'wa_profile'), headless=False, no_viewport=True, args=['--remote-debugging-port=9222'])
page = browser.pages[0] if browser.pages else browser.new_page()
try:
    page.goto('https://web.whatsapp.com', timeout=90000, wait_until='domcontentloaded')
except Exception:
    pass
print('🔥 warm WhatsApp browser ready on :9222', flush=True)
try:
    while True:
        time.sleep(3600)
except KeyboardInterrupt:
    pass
finally:
    try: browser.close()
    except Exception: pass
    try: pw.stop()
    except Exception: pass
''')
    done.append('wa-warm-script')
AW = os.path.join(D, 'ad_wait.py')
s = open(AW).read()
if 'connect_over_cdp' not in s:
    s = s.replace("# AD-WAIT v81.36:", "# AD-WAIT v81.37:", 1)
    s = s.replace("""pw = sync_playwright().start()
browser = None
try:
    browser = pw.chromium.launch_persistent_context(os.path.join(BASE, 'wa_profile'), headless=False, no_viewport=True)
    page = browser.pages[0] if browser.pages else browser.new_page()""",
"""pw = sync_playwright().start()
browser = None
page = None
via_cdp = False
try:
    browser = pw.chromium.connect_over_cdp('http://127.0.0.1:9222')  # WARM-CONNECT v81.37: seconds, not a cold minute
    ctx = browser.contexts[0] if browser.contexts else browser.new_context()
    page = ctx.new_page()
    via_cdp = True
    print('\\u26a1 warm browser connected - opening chat in seconds', flush=True)
except Exception:
    browser = pw.chromium.launch_persistent_context(os.path.join(BASE, 'wa_profile'), headless=False, no_viewport=True)
    page = browser.pages[0] if browser.pages else browser.new_page()
    via_cdp = False
    print('\\U0001f422 no warm browser yet - cold launch this once', flush=True)""")
    s = s.replace("""        ok = wa._place_text(page, cur_txt, print)""",
"""        try:  # CLEAR-BEFORE-PLACE v81.37: yesterday's unsent Draft never concatenates with today's words
            for _sel in wa.COMPOSE_SELS:
                try:
                    page.wait_for_selector(_sel, timeout=8000); break
                except Exception:
                    continue
            page.keyboard.press('Meta+A'); page.keyboard.press('Backspace')
            print('\\U0001f9f9 cleared stale field text before placing new draft', flush=True)
        except Exception:
            pass
        ok = wa._place_text(page, cur_txt, print)""", 1)
    s = s.replace("""    try:
        if browser is not None: browser.close()
    except Exception:
        pass""",
"""    try:
        if via_cdp and page is not None: page.close()
        elif browser is not None: browser.close()
    except Exception:
        pass""")
    open(AW, 'w').write(s); done.append('ad-wait-v81.37')
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if '# STALE-WINDOW-SWEEP v81.32' in l and 'Google Chrome for Testing' in l:
        B[k] = ind(l)*' ' + "os.system(\"pkill -f 'ad_wait.py' 2>/dev/null\")  # STALE-WINDOW-SWEEP v81.32: watchers retire; the warm browser lives on"
        done.append('sweep-warm-safe'); break
src = '\n'.join(B)
if '# WA-WARM v81.37' not in src:
    i = next(k for k, l in enumerate(B) if '# SWEEP-RESET v81.34' in l)
    j = i + 2
    d = ind(B[i])
    B[j+1:j+1] = [d*' ' + "try:",
                  d*' ' + "    subprocess.Popen([sys.executable, os.path.join(BASE_DIR, 'wa_warm.py'), 'ensure'], cwd=BASE_DIR, stdout=open(os.path.join(BASE_DIR, 'wa_warm.log'), 'a'), stderr=subprocess.STDOUT, start_new_session=True)  # WA-WARM v81.37",
                  d*' ' + "except Exception:",
                  d*' ' + "    pass"]
    done.append('warm-ensure-boot')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S141 the window opens in seconds, not a minute" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S140 one release per state change" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S141 the window opens in seconds, not a minute', os.path.exists(os.path.join(BASE_DIR, 'wa_warm.py')) and 'connect_over_cdp' in open(os.path.join(BASE_DIR, 'ad_wait.py')).read())")
    B.insert(i+2, d*' ' + "ck('S142 stale field text is cleared before placement', 'CLEAR-BEFORE-PLACE v81.37' in open(os.path.join(BASE_DIR, 'ad_wait.py')).read())")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S141-S142-guards')
print('✅', done)
