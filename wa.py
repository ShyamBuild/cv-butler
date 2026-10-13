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
        page.goto("https://web.whatsapp.com")
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

def send_review(phone, text, say=print, ask=None):
    _ask = ask or input
    page = ensure_login(say)
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10: digits = '91' + digits
    page.goto(f"https://web.whatsapp.com/send?phone={digits}")
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
        try: c = _ask("   [Enter] send · [e] edit msg · [n] fix number · [q] skip: ").strip()
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
            page.goto(f"https://web.whatsapp.com/send?phone={digits}")
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
        if c == '':
            box = page.locator('div[data-testid="conversation-compose-box-input"]')
            box.click()
            try: box.fill(text)
            except Exception: page.keyboard.type(text, delay=5)
            sent = False
            for sel in ('button[data-testid="compose-btn-send"]', 'span[data-icon="btn-send"]'):
                try:
                    page.locator(sel).first.click(timeout=3000); sent = True; break
                except Exception: continue
            say("✅ sent via WhatsApp Web" if sent else "⚠️ send-button not found - click send yourself in the WA window")
            return sent

def close():
    try:
        if _state.get('ctx'): _state['ctx'].close()
    except Exception:
        pass
    try:
        if _state.get('pw'): _state['pw'].stop()
    except Exception:
        pass
    _state.clear()
