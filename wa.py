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

COMPOSE_SELS = ('footer div[contenteditable="true"][data-tab="10"]', 'footer div[contenteditable="true"][data-lexical-editor="true"]', 'footer div[contenteditable="true"]', 'footer div[contenteditable="true"]')
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

def _key(prompt):  # ONE-KEY v84.46: the menu answers to the keystroke alone; Enter still means take your time
    import sys, termios, tty
    if getattr(sys.stdout, 'last', '\n') != '\n': sys.stdout.write('\r\n')  # NEWLINE-DISCIPLINE v85.18  # CRLF-RAW v85.22: in raw mode the writer is the driver - LF alone leaves the column where it stood
    sys.stdout.write(prompt); sys.stdout.flush()
    try:
        fd = sys.stdin.fileno(); old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd); k = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    except Exception:
        return (input() or '').strip().lower()
    if k in ('\r', '\n'):
        sys.stdout.write('\r\n'); sys.stdout.flush(); return ''  # CRLF-RAW v85.22: in raw mode the writer is the driver - LF alone leaves the column where it stood
    sys.stdout.write(k + '\r\n'); sys.stdout.flush()  # CRLF-RAW v85.22: in raw mode the writer is the driver - LF alone leaves the column where it stood
    return k.strip().lower()

def _send_review_body(phone, text, say=print, ask=None):
    try:
        import asyncio as _a
        import asyncio as _a  # QUIET-ASYNCIO v85.28  # POLICY-RESET v85.25  # LOOP-CLEAN v85.21: whichever probe this playwright consults, the ritual supplies the quiet room itself - default policy, private idle loop, and both asyncio probes shadowed to tell the truth a clean process would tell
        _q = _a.new_event_loop()
        _a.set_event_loop_policy(_a.DefaultEventLoopPolicy())
        _a.set_event_loop(_q)
        def _no_running(*_a2, **_k2):
            raise RuntimeError('no running event loop')
        _a.get_running_loop = _no_running
        _a.get_event_loop = lambda *_a2, **_k2: _q
    except Exception:
        pass
    digits = re.sub(r'\D', '', str(phone))
    if len(digits) == 10: digits = '91' + digits
    say(f"🌐 opening WhatsApp Web in the BUTLER window for +{digits}…")
    if os.environ.get('WA_DIAG'):  # WA-DIAG v85.28: when the window still refuses, the body confesses the loop's true face before the call
        import asyncio as _d
        try:
            _d.get_running_loop(); print('DIAG: running loop PRESENT')
        except RuntimeError:
            print('DIAG: no running loop')
        try:
            print('DIAG: get_event_loop().is_running() =', _d.get_event_loop().is_running())
        except Exception as _e:
            print('DIAG: get_event_loop raised', _e)
        try:
            print('DIAG: policy =', type(_d.get_event_loop_policy()).__name__)
        except Exception:
            pass
    pw = sync_playwright().start()
    browser = None
    page = None
    via_cdp = False
    try:
        try:
            _door = pw.chromium.connect_over_cdp('http://127.0.0.1:9222')  # WARM-CLIENT v81.47 + v81.55: the shared door is never ours to query or close
            _ctx2 = _door.contexts[0] if _door.contexts else _door.new_context()
            page = _ctx2.new_page()
            via_cdp = True
            browser = None
        except Exception:
            ctx = _ctx()  # PERSISTENT-WA v84.38: reuse the living window instead of launching and closing one per draft
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            via_cdp = False
        if not _goto(page, f"https://web.whatsapp.com/send?phone={digits}", say):
            say('⚠️ chat page did not load - scan QR in the opened window if asked, then retry')
            return False
        try:
            _html = page.content()
        except Exception:
            _html = ''
        if ('Link your phone' in _html or 'qr code' in _html.lower()) and 'conversation' not in _html:  # QR-RESCAN v85.26: a logged-out window asks for one scan, named aloud, instead of failing as a library complaint
            say('🔐 WhatsApp Web is logged out in the BUTLER window - scan the QR with your phone once, then press any key here')
            _key('')
            try:
                page.reload(wait_until='domcontentloaded', timeout=60000)
                _goto(page, f'https://web.whatsapp.com/send?phone={digits}', say)
            except Exception:
                pass
        try:
            try:  # EARLY-DOOR v81.92: ask WhatsApp within the first beats, not after the placement wait - poll four seconds for the modal or the field, whichever speaks first (inserted before the modal-check if, at its own indent; the late path stays as fallback)
                for _i in range(48):  # MODAL-WATCH v81.98: the door is asked until it answers - twenty-four beats, not four; the modal confesses, the composer releases, and only true ambiguity pays the full count
                    _html = page.content() or ''
                    if "isn't on WhatsApp" in _html:
                        say('⚠️ WhatsApp says this number isn\'t on WhatsApp - nothing drafted; teach or re-pick a number that is registered, or close the window whenever you like')
                        return False
                    try:
                        if page.locator('footer div[contenteditable="true"]').count() > 0: break
                    except Exception: break
                    page.wait_for_timeout(500)
            except Exception:
                pass
            if "isn't on WhatsApp" in (page.content() or ''):
                say('⚠️ WhatsApp says this number is not registered - nothing drafted. Correct it with: fixphone <name> <10-digit>')
                return False
        except Exception:
            pass
        ok_fill = _place_text(page, text, say)
        if not ok_fill:
            _notwa = False  # CONCISE v81.91: the paste advice is wrong when WhatsApp has already said there is no field
            try:  # NOT-ON-WHATSAPP v81.90: WhatsApp's own words beat any guess - say them plainly before advising a paste into a field that does not exist
                if "isn't on WhatsApp" in (page.content() or ''):
                    say('⚠️ WhatsApp says this number isn\'t on WhatsApp - there is no message field to paste into; [x] discards this round, [q] closes it, or teach/re-pick a number that is registered')
                    _r = input('   [x] discard this round · [q] close the window · [Enter] keep it open, then teach or re-pick: ').strip().lower()  # NO-FIELD-EXIT v81.94: a dead number ends the round with ONE menu; the paste-advice never speaks after a no-field confession
                    if _r == 'q':
                        try: page.close()
                        except Exception: pass
                    return False
                    _notwa = True
            except Exception: pass
            if not _notwa: say('⚠️ field did not take the text automatically - paste the draft from above into the WhatsApp field yourself, then:')
        if os.path.exists(AUTOSEND):
            sent = _click_send(page)
            say('✅ sent via WhatsApp Web (autosend)' if sent else '⚠️ send-button not found - click send yourself in the WA window')
            if sent: _arm(digits, text)
            return bool(sent)
        say("📝 message is in the WhatsApp text field - the window STAYS open until you choose:")
        while True:
            _pm = '[s] I clicked send myself · [x] discard & clear · [q] leave in field & close · [Enter] keep waiting: '  # FLUSH-CUE v85.14
            c = (ask(_pm).strip().lower() if ask else _key(_pm))  # ONE-KEY v84.46
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
        return True
    except Exception as e:
        say(f'⚠️ whatsapp failed: {e}')
        return False
    finally:
        try:
            if via_cdp and page is not None: page.close()
            pass  # PERSISTENT-WA v84.38: the persistent browser is never closed; only a CDP guest page goes home
        except Exception:
            pass
        try:
            if via_cdp: pw.stop()  # PERSISTENT-WA v84.38: only the CDP playwright instance stops; the living one rests in _state
        except Exception:
            pass


def send_review(phone, text, say=print, *a, **k):  # PLAYWRIGHT-THREAD v85.23  # PLAYWRIGHT-PROCESS v85.24: the ritual runs in a brand-new process - born without loops or policies - inheriting the tty so bare keys still answer; the exit code carries the truth home
    import subprocess, sys
    code = 'import sys, wa; sys.exit(0 if wa._send_review_body(%r, %r, print) else 1)' % (phone, text)
    r = subprocess.call([sys.executable, '-c', code], cwd=os.path.dirname(os.path.abspath(__file__)))
    if r != 0:
        say('⚠️ whatsapp failed in its own process - retry with: python3 -c "import wa; wa._send_review_body(' + repr(phone) + ', ' + repr(text) + ', print)"')
        try:  # PARK-DRAFT v85.27: a broken window must never cost a courtesy - the exact draft parks by phone and names its own path
            pd = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drafts', 'parked')
            os.makedirs(pd, exist_ok=True)
            fn = os.path.join(pd, re.sub(r'\D', '', str(phone)) + '.txt')
            open(fn, 'w').write(text)
            say('📥 draft parked at ' + fn + ' - send it by hand or retry once the window is cured')
        except Exception:
            pass
        return False
    return True