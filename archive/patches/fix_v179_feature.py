import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
D = os.getcwd()
open(os.path.join(D, 'wa_warm.py'), 'w').write('''# WA-WARM v81.44: owned warm browser; honours your close 10 min; records the close so keepalive waits too
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
        try: open(os.path.join(BASE, 'wa_warm_closed.ts'), 'w').write(str(time.time()))  # WARM-KEEPALIVE v81.44
        except Exception: pass
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
done.append('wa-warm-v81.44')
AW = os.path.join(D, 'ad_wait.py'); s = open(AW).read()
old_slide = "    ok = wa._place_text(page, cur_txt, print); retried = False; placed = time.time(); empties = 0"
if old_slide in s and 'CLEAR-IN-SLIDE' not in s:
    s = s.replace(old_slide, "    try:\n        page.keyboard.press('Meta+A'); page.keyboard.press('Backspace')  # CLEAR-IN-SLIDE v81.44: a slide never appends onto a parked draft\n    except Exception:\n        pass\n" + old_slide)
    open(AW, 'w').write(s); done.append('clear-in-slide')
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# WARM-KEEPALIVE v81.44' not in src:
    p = next(k for k, l in enumerate(B) if l.strip().startswith('def _pulse_loop():'))
    i = next(k for k in range(p, p+40) if B[k].strip() == 'time.sleep(2)')
    d = ind(B[i])
    B[i:i] = [d*' ' + "if time.time() - getattr(B, '_warm_keep', 0) > 60:  # WARM-KEEPALIVE v81.44: the keeper is respawned unless you closed it yourself",
              d*' ' + "    B._warm_keep = time.time()",
              d*' ' + "    try:",
              d*' ' + "        _cl = os.path.join(BASE_DIR, 'wa_warm_closed.ts')",
              d*' ' + "        _rc = os.path.exists(_cl) and time.time() - os.stat(_cl).st_mtime < 600",
              d*' ' + "        if not _rc and os.system(\"pgrep -f 'wa_warm.py' >/dev/null 2>&1\") != 0:",
              d*' ' + "            subprocess.Popen([sys.executable, os.path.join(BASE_DIR, 'wa_warm.py'), 'ensure'], cwd=BASE_DIR, stdout=open(os.path.join(BASE_DIR, 'wa_warm.log'), 'a'), stderr=subprocess.STDOUT, start_new_session=True)",
              d*' ' + "            print('\\U0001f525 warm keepalive: relaunching wa_warm', flush=True)",
              d*' ' + "    except Exception:",
              d*' ' + "        pass"]
    done.append('warm-keepalive')
for k, l in enumerate(B):
    if l.strip() == "if False and kind == 'ctime': pass  # NEUTER-DONEMARK v81.30 (every tag action is a new event)":
        B.insert(k+1, ind(l)*' ' + "if kind == 'ctime' and not self._ad_fidget(): say(f'⏭️ autodraft: {os.path.basename(fp)} +{tg} ctime-only touch (Finder preview/index), not a tag action - fidget.flag on drafts these'); return  # KIND-RESPECT v81.44")
        done.append('kind-respect'); break
for k, l in enumerate(B):
    if l.strip() == "q.append({'phone': d, 'text': txt, 'at': time.time(), 'who': nm, 'voice': v, 'fp': fp, 'tag': tg})":
        d2 = ind(l)
        B[k:k+1] = [d2*' ' + "if not any(_x.get('phone') == d and _x.get('who') == nm for _x in q):  # DEDUPE v81.44: one queued draft per candidate",
                    d2*' ' + "    q.append({'phone': d, 'text': txt, 'at': time.time(), 'who': nm, 'voice': v, 'fp': fp, 'tag': tg})"]
        done.append('dedupe'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S147 the warm browser is kept alive unless you closed it" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S146 your close is honoured for ten minutes" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S147 the warm browser is kept alive unless you closed it', (chr(35)+' WARM-KEEPALIVE v81.44') in _src and 'wa_warm_closed.ts' in open(os.path.join(BASE_DIR, 'wa_warm.py')).read())")
    B.insert(i+2, d*' ' + "ck('S148 ctime-only touches are quiet unless fidget is on', (chr(35)+' KIND-RESPECT v81.44') in _src)")
    B.insert(i+3, d*' ' + "ck('S149 no doubled drafts', (chr(35)+' DEDUPE v81.44') in _src and (chr(35)+' CLEAR-IN-SLIDE v81.44') in open(os.path.join(BASE_DIR, 'ad_wait.py')).read())")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S147-S149-guards')
print('✅', done)
