import os, re, time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE = os.path.join(BASE_DIR, "wa_profile")
_state = {}

try:
    from playwright.sync_api import sync_playwright
except Exception:
    sync_playwright = None

def _ctx():
    if 'ctx' not in _state:
        from playwright.sync_api import sync_playwright
        pw = sync_playwright().start()
        ctx = pw.chromium.launch_persistent_context(
            PROFILE, headless=False, viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled"])
        _state['pw'] = pw; _state['ctx'] = ctx
    return _state['ctx']

def _logged_in(page):
    try:
        return page.locator('div[data-testid="chat-list"]').count() > 0
    except Exception:
        return False

def ensure_login(say=print):
    ctx = _ctx()
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    if 'whatsapp' not in (page.url or ''):
        _goto(page, "https://web.whatsapp.com")
    told = False
    for _ in range(150):
        if _logged_in(page): return page
        if not told and page.locator('canvas').count():
            say("📱 SCAN THE QR once: phone -> WhatsApp -> Settings -> Linked Devices")
            told = True
        time.sleep(2)
    raise RuntimeError("WhatsApp login timed out - try again")

_SEND_SELS = ('button[data-testid="compose-btn-send"]', 'div[data-testid="compose-btn-send"]',
              'span[data-icon="btn-send"]', 'button[aria-label="Send"]', 'button[aria-label*="send"]',
              'span[data-icon="send"]')
def _click_send(page):
    for sel in _SEND_SELS:
        try:
            page.locator(sel).first.click(timeout=3000); return True
        except Exception:
            continue
    return False

def _goto(page, url, say=print):
    for a in (0, 1):
        try:
            page.goto(url, timeout=90000, wait_until='domcontentloaded'); return True
        except Exception:
            if a == 0: time.sleep(2)
    say('⚠️ WhatsApp page did not load (network?) - try again in a minute')
    return False

AUTOSEND = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', '.autosend')

COMPOSE_SELS = ('div[contenteditable="true"][data-tab="10"]', 'div[contenteditable="true"][data-lexical-editor="true"]', 'footer div[contenteditable="true"]', 'div[contenteditable="true"]')
def _place_text(page, text, say=print):
    for attempt in (0, 1, 2):
        try:
            box = None
            for sel in COMPOSE_SELS:
                try:
                    page.wait_for_selector(sel, timeout=8000)
                    box = sel; break
                except Exception:
                    continue
            if not box: continue
            page.click(box)
            page.keyboard.insert_text(text)
            page.wait_for_timeout(400)
            got = page.eval_on_selector(box, "e => e.innerText || e.textContent || ''")
            if got and got.strip() and text.split()[0].lower() in got.lower():
                return True
        except Exception:
            pass
        page.wait_for_timeout(1200)
    return False

def _arm(phone, text):
    try:
        import cadence
        m = re.match(r"\s*Hi\s+([A-Za-z][A-Za-z .\-]+?),", text or "")
        cadence.arm(phone, (m.group(1).strip() if m else None))
    except Exception:
        pass

def send_review(phone, text, say=print, ask=None):
    digits = re.sub(r'\D', '', str(phone))
    if len(digits) == 10: digits = '91' + digits
    say(f"🌐 opening WhatsApp Web in the BUTLER window for +{digits}…")
    pw = sync_playwright().start()
    browser = None
    page = None
    try:
        browser = pw.chromium.launch_persistent_context(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wa_profile'), headless=False, no_viewport=True)
        page = browser.pages[0] if browser.pages else browser.new_page()
        if not _goto(page, f"https://web.whatsapp.com/send?phone={digits}", say):
            say('⚠️ chat page did not load - scan QR in the opened window if asked, then retry')
            return False
        try:
            if "isn't on WhatsApp" in (page.content() or ''):
                say('⚠️ WhatsApp says this number is not registered - nothing drafted. Correct it with: fixphone <name> <10-digit>')
                return False
        except Exception:
            pass
        ok_fill = _place_text(page, text, say)
        if not ok_fill:
            say('⚠️ field did not take the text automatically - paste the draft from above into the WhatsApp field yourself, then:')
        if os.path.exists(AUTOSEND):
            sent = _click_send(page)
            say('✅ sent via WhatsApp Web (autosend)' if sent else '⚠️ send-button not found - click send yourself in the WA window')
            if sent: _arm(digits, text)
            if sent: _arm(digits, text)
            return bool(sent)
        say('📝 message is in the WhatsApp text field - review it in the opened window, then:')
        say("📝 message is in the WhatsApp text field - the window STAYS open until you choose:")
        while True:
            c = (ask or input)("   [s] I clicked send myself · [x] discard & clear · [q] leave in field & close · [Enter] keep waiting: ").strip().lower()
            if c == '':
                say("   …still open - take your time (s / x / q)")
                continue
            break
        if c == 'x':
            try:
                page.keyboard.press('Meta+A'); page.keyboard.press('Backspace')
            except Exception:
                pass
            say('🗑 discarded - nothing sent')
            return False
        if c == 'q':
            say('📝 left in field & window closed - NOT counted as sent')
            return False
        say('✅ sent (you clicked in WhatsApp)')
        _arm(digits, text)
        _arm(digits, text)
        return True
    except Exception as e:
        say(f'⚠️ whatsapp failed: {e}')
        return False
    finally:
        try:
            if browser is not None: browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass
