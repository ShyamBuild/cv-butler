# WA-WARM v81.45: owned warm browser with a circuit-breaker - it may die, it may not flicker
import os, sys, time
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
if len(sys.argv) > 1 and sys.argv[1] == 'ensure':
    from playwright.sync_api import sync_playwright
    try:
        pw = sync_playwright().start()
        b = pw.chromium.connect_over_cdp('http://127.0.0.1:9222', timeout=5000)  # COLD-CLOSURE v85.165: a half-alive door must refuse in five seconds, never hang an hour
        print('warm browser already alive', flush=True); pw.stop(); sys.exit(0)
    except Exception:
        try: pw.stop()
        except Exception: pass
from playwright.sync_api import sync_playwright
fails = 0
while True:
    pw = sync_playwright().start()
    t0 = time.time()
    try:
        browser = pw.chromium.launch_persistent_context(os.path.join(BASE, 'wa_profile'), headless=False, no_viewport=True, args=['--remote-debugging-port=9222'])
        page = browser.pages[0] if browser.pages else browser.new_page()
        try:
            page.goto('https://web.whatsapp.com', timeout=90000, wait_until='domcontentloaded')
        except Exception:
            pass
        print('\U0001f525 warm WhatsApp browser ready on :9222', flush=True)
        fails = 0
        _closed = []
        try: browser.on('close', lambda: _closed.append(1))  # CLOSE-WATCH v81.46
        except Exception: pass
        while True:  # CLOSE-WATCH v81.46: a BrowserContext has no is_connected - probe closure instead of assuming an API
            time.sleep(3)
            try:
                if _closed: break
                _ = browser.pages
            except Exception:
                break
        try: open(os.path.join(BASE, 'wa_warm_closed.ts'), 'w').write(str(time.time()))  # WARM-KEEPALIVE v81.44
        except Exception: pass
        print('\U0001f44b closed by you; staying closed for 10 min (drafts cold-launch meanwhile)  # WARM-COOLDOWN v81.41', flush=True)
        try: pw.stop()
        except Exception: pass
        time.sleep(600)
        continue
    except Exception as e:
        fails += 1
        print(f'\u26a0\ufe0f warm browser failed ({fails} in a row): {e}', flush=True)
        try: os.system("pkill -f 'Google Chrome for Testing' 2>/dev/null")  # BREAKER-SWEEP v81.45: ownerless zombies cannot poison the retry
        except Exception: pass
    finally:
        try: pw.stop()
        except Exception: pass
    if time.time() - t0 < 30 and fails >= 3:
        print('\u26a0\ufe0f warm browser crash-looping; backing off 5 min (drafts cold-launch meanwhile)  # BREAKER v81.45', flush=True)
        fails = 0
        time.sleep(300)
    else:
        time.sleep(10)
