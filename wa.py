import os, re, time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE = os.path.join(BASE_DIR, "wa_profile")
_state = {}

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

def send_review(phone, text, say=print, ask=None):
    _ask = ask or input
    page = ensure_login(say)
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10: digits = '91' + digits
    if not _goto(page, f"https://web.whatsapp.com/send?phone={digits}"): return False
    try:
        page.wait_for_selector('div[data-testid="conversation-compose-box-input"]', timeout=60000)
    except Exception:
        say("⚠️ chat box did not open (wrong number?) - skipped")
        return False
    say("")
    say(f"🤖 draft -> {digits}:")
    for ln in text.split("\n"): say("   " + ln)
    if os.path.exists(os.path.join(BASE_DIR, 'templates', '.autosend')):
        box = page.locator('div[data-testid="conversation-compose-box-input"]')
        box.click()
        try: box.fill(text)
        except Exception: page.keyboard.type(text, delay=5)
        sent = _click_send(page)
        say("✅ auto-sent via WhatsApp Web" if sent else "⚠️ auto-send could not click send - message left in the box for you")
        return sent
    while True:
        try: c = _ask("   [Enter] put in WhatsApp field (you send) · [e] edit msg · [n] fix number · [q] skip: ").strip()
        except EOFError: return False
        if c.lower() == 'q':
            say("⏭ skipped"); return False
        if c.lower() == 'n':
            _a = locals().get('_ask', input)
            nn = _a("   correct 10-digit number (paste with or without +91): ").strip()
            d2 = re.sub(r'\D', '', nn)
            if len(d2) == 10: d2 = '91' + d2
            if not re.fullmatch(r'91[6-9]\d{9}', d2):
                say("   ⚠️ not a valid Indian mobile - keeping previous number"); continue
            digits = d2
            if not _goto(page, f"https://web.whatsapp.com/send?phone={digits}"): return False
            try:
                page.wait_for_selector('div[data-testid="conversation-compose-box-input"]', timeout=60000)
            except Exception:
                say("   ⚠️ chat box did not open for the new number"); continue
            say(f"   📞 sending to {d2[2:]} instead - draft unchanged below")
            continue
        if c.lower() == 'e':
            nt = _ask("   new message: ").strip()
            if nt: text = nt
            continue
        say('🌐 opening WhatsApp Web in the BUTLER window - wait for the chat to load…')
        pw = sync_playwright().start()
        browser = None
        c2 = ''
        try:
            browser = pw.chromium.launch_persistent_context(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wa_profile'), headless=False, no_viewport=True)
            page = browser.pages[0] if browser.pages else browser.new_page()
            if not _goto(page, f"https://web.whatsapp.com/send?phone={digits}"):
                say('⚠️ chat page did not load - scan QR in the opened window if asked, then retry')
                return False
            box = None
            for s in ('div[contenteditable="true"][data-tab="10"]', 'div[contenteditable="true"][data-lexical-editor="true"]', 'footer div[contenteditable="true"]'):
                try:
                    page.wait_for_selector(s, timeout=45000); box = page.locator(s).first; break
                except Exception:
                    continue
            if box is None:
                say('⚠️ compose box not found in the butler window - retry once the chat is open')
                return False
            box.click()
            page.keyboard.insert_text(text)
            if os.path.exists(AUTOSEND):
                sent = _click_send(page)
                if sent: page.wait_for_timeout(1500)
                say('✅ sent via WhatsApp Web (autosend)' if sent else '⚠️ send-button not found - click send yourself in the WA window')
                return sent
            say('📝 draft is now in the BUTLER window text field - review it THERE, click send yourself, then answer here:')
            c2 = (ask or input)('   [Enter] I clicked send myself · [x] discard & clear: ').strip().lower()
            if c2 == 'x':
                try:
                    page.keyboard.press('Meta+A'); page.keyboard.press('Backspace')
                except Exception:
                    pass
                say('🗑 discarded - nothing sent')
                return False
            say('✅ sent (you clicked in WhatsApp)')
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