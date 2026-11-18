import os, re, time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_CDP_URL = os.environ.get('CV_WA_CDP_URL') or ('http://127.0.0.1:' + os.environ.get('CV_WA_CDP_PORT', '9222'))  # OFFLINE-CONFIG v85.176: the warm door's address, overridable, never a second browser service
PROFILE = os.path.join(BASE_DIR, "wa_profile")
_state = {}

try:
    from playwright.sync_api import sync_playwright
except Exception:
    sync_playwright = None

_PW = [None]
def _pw():  # ONE-START v85.30: playwright is started once per process and shared by every door - the ladder proved a second sync start is the library's forbidden door, and its complaint about asyncio was a lie about arity
    if _PW[0] is None:
        from playwright.sync_api import sync_playwright
        _PW[0] = sync_playwright().start()
    return _PW[0]

LAST_FAIL = ['']  # EPIPE-INPROC v85.150: the door's last refusal in one word - 'lock' when Chrome held the profile, 'dead' when WhatsApp said the number is not there


class WaBusy(RuntimeError):  # PROFILE-LOCK v85.150: a held profile is a sentence the master can act on, never a traceback
    pass


def _pw_fresh():  # PLAYWRIGHT-FRESH v85.185  # ALIVE-FLAG v85.186: a dead driver is cleared before any door is handed one
    try:
        if not _state.get('alive'):
            _PW[0] = None
            _state.pop('ctx', None)
    except Exception:
        pass
    _p = _pw()
    _state['alive'] = True
    return _p
def _lock_words(e):  # PROFILE-LOCK v85.150: the shapes playwright wears when another Chrome already owns wa_profile
    t = ('%r' % (e,)).lower()
    return any(w in t for w in ('processsingleton', 'singletonlock', 'already in use', 'is already running', 'profile directory', 'user data directory'))


def _lock_owner_pid():  # WARM-REUSE v85.177: the profile lock names its owner as <host>-<pid>; read it, never guess
    try:
        _t = os.readlink(os.path.join(PROFILE, 'SingletonLock'))
        return int(str(_t).rsplit('-', 1)[1])
    except Exception:
        return 0
def _pid_alive(pid):  # WARM-REUSE v85.177: a pid that answers kill(0) is holding a real window
    try:
        os.kill(int(pid), 0)
        return True
    except Exception:
        return False
def _reap_stale_lock():  # WARM-REUSE v85.177: a lock whose owner is gone is litter - remove it so the next launch can live
    try:
        _pid = _lock_owner_pid()
        if _pid and not _pid_alive(_pid):
            for _f in ('SingletonLock', 'SingletonSocket', 'SingletonCookie'):
                try:
                    os.unlink(os.path.join(PROFILE, _f))
                except Exception:
                    pass
            print('🧹 stale WhatsApp profile lock removed (owner is gone)', flush=True)
            return True
    except Exception:
        pass
    return False

def _ctx():
    if 'ctx' not in _state:
        pw = _pw_fresh()  # PLAYWRIGHT-FRESH v85.185: a live instance or a new one, never a stopped one
        _reap_stale_lock()  # WARM-REUSE v85.177: reap before launching, so a dead owner never blocks the living one
        try:
            ctx = pw.chromium.launch_persistent_context(
                PROFILE, headless=False, viewport={"width": 1280, "height": 900},
                args=["--disable-blink-features=AutomationControlled"])
        except Exception as e:  # PROFILE-LOCK v85.150: Chrome is already open on wa_profile - catch it, name the cure, never crash the chat
            if _lock_words(e):
                try:  # WARM-REUSE v85.177: a held profile with a live door is not a wall - it is the window the house already owns
                 _door = pw.chromium.connect_over_cdp(_CDP_URL)
                 _ctx2 = _door.contexts[0] if _door.contexts else _door.new_context()
                 _state['pw'] = pw
                 _state['ctx'] = _ctx2
                 return _ctx2
                except Exception:
                 raise WaBusy('🔒 the WhatsApp window is open but its door is shut (profile lock on wa_profile). Repeat the same command in a moment - nothing was sent, nothing was lost.') from None
            raise
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

def wa_goto(phone, say=print):  # WA-GOTO v85.150: the prep door the seat already calls - digits only, and honest when the window refuses
    try:
        ctx = _ctx()
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        url = 'https://web.whatsapp.com/send?phone=' + re.sub(r'\D', '', str(phone))
        return _goto(page, url, say)
    except WaBusy as e:  # PROFILE-LOCK v85.150: the master's cure, not a traceback
        say(str(e))
        return False
    except Exception as e:
        say(f'⚠️ wa_goto failed for phone {phone}: {e}')
        return False

def _arm_dialogs(page, say=None):  # DIALOG-ARM v85.179  # DIALOG-SAFE v85.206: the answer can never crash the driver
    try:
        if getattr(page, '_butler_dialogs', False):
            return True
        def _answer(_dlg):
            try:
                _dlg.accept()
            except Exception:
                pass  # DIALOG-SAFE v85.206: a dialog that closed first is not an error - and never an uncaught one
        page.on('dialog', _answer)
        try:
            page._butler_dialogs = True
        except Exception:
            pass
        return True
    except Exception:
        return False

def _goto(page, url, say=print):  # GOTO-CONFESS v85.195: a failed navigation names its own reason, once
    _arm_dialogs(page)  # DIALOG-ARM v85.179: every goto answers the leave-page question first
    _errs = []
    for _a, _mode in enumerate((('commit', 45000), ('domcontentloaded', 60000))):
        try:
            page.goto(url, timeout=_mode[1], wait_until=_mode[0])
            return True
        except Exception as _ge:
            _errs.append(repr(_ge)[:120])
            if _a == 0:
                time.sleep(2)
    if _errs:
        say('⚠️ WhatsApp page did not load - %s' % _errs[-1])  # GOTO-CONFESS v85.195: the real reason, not a guess
    return False

AUTOSEND = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', '.autosend')

COMPOSE_SELS = ('footer div[contenteditable="true"][data-tab="10"]', 'footer div[contenteditable="true"][data-lexical-editor="true"]', 'footer div[contenteditable="true"]', 'footer div[contenteditable="true"]')

def _page_alive(page):  # DIALOG-SAFE v85.206: a page can be closed under us - ask before believing it
    try:
        return page is not None and (page.url or None) is not None
    except Exception:
        return False
def _fresh_page(say=None):  # DIALOG-SAFE v85.206: after a TargetClosed, one re-arm from the warm door
    try:
        pw = _pw_fresh()
        _door = pw.chromium.connect_over_cdp(_CDP_URL)
        _c = _door.contexts[0] if _door.contexts else _door.new_context()
        _pgs = [x for x in _c.pages if 'web.whatsapp.com' in (getattr(x, 'url', '') or '')]
        _pg = _pgs[0] if _pgs else (_c.pages[0] if _c.pages else _c.new_page())
        _arm_dialogs(_pg, say)
        return _pg
    except Exception:
        return None

def _composer_ready(page, timeout=30000):  # COMPOSER-WAIT v85.150: the field is waited for as a visible truth, so a slow load never wears the coat of a dead number
    for sel in COMPOSE_SELS:
        try:
            page.wait_for_selector(sel, state='visible', timeout=timeout)
            return sel
        except Exception:
            continue
    return ''


def _no_wa_modal(page):  # NOT-ON-WHATSAPP v81.90  # MODAL-CONFIRM v85.150: only a VISIBLE dialog may pronounce a number absent - a hidden template that merely carries the words is not a verdict
    try:
        loc = page.get_by_text("isn't on WhatsApp", exact=False)
        total = loc.count()
    except Exception:
        return False
    for _i in range(min(total, 6)):
        try:
            if loc.nth(_i).is_visible():
                return True
        except Exception:
            continue
    return False


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
            try:  # FIELD-CLEAR v85.34: the persistent composer keeps yesterday's sentence unless the ritual empties it first - select-all and delete before every fill
                page.keyboard.press('Meta+a')
                page.keyboard.press('Delete')
            except Exception:
                pass
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

def watest(say=print):  # WA-STEP v85.29: each door of the ritual opened in order and named aloud, with a QR pause the moment one is visible - the master's instinct, made a ladder
    from playwright.sync_api import sync_playwright
    say('1 start…')
    pw = _pw_fresh()  # PLAYWRIGHT-FRESH v85.185: a live instance or a new one, never a stopped one
    say('1 ok')
    page = None
    try:
        say('2 cdp connect…')
        d = pw.chromium.connect_over_cdp(_CDP_URL)
        page = (d.contexts[0] if d.contexts else d.new_context()).new_page()
        say('2 ok - the shared warm door answered')
    except Exception as e:
        say('2 cdp refused: %r - opening the persistent BUTLER window' % (e,))
        ctx = _ctx()
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        say('2 ok - persistent window opened')
    try:
        say('3 goto whatsapp…')
        page.goto('https://web.whatsapp.com/', timeout=60000)
        say('3 ok')
    except Exception as e:
        say('3 goto refused: %r' % (e,))
        return False
    html = page.content()
    if 'Link your phone' in html or 'qr code' in html.lower():
        say('🔐 QR visible - scan it now with your phone; the window stays open; press any key when linked')
        _key('')
        try:
            page.reload(timeout=60000)
        except Exception:
            pass
        html = page.content()
    ok = ('conversation' in html) or ('chat' in html.lower()) or ('Link your phone' not in html and 'qr code' not in html.lower())
    say('4 logged-in markers present: %s' % ok)
    say('watest complete - the window stays open for the next send')
    return bool(ok)

def _tab_free(pg):  # DRAFT-TAB v85.190: a tab holding a draft belongs to the master - the next deed must not navigate it away
    try:
        _sel = 'footer div[contenteditable="true"]'
        if pg.locator(_sel).count() == 0:
            return True
        return not (pg.locator(_sel).first.inner_text() or '').strip()
    except Exception:
        return True

def preopen(phone, say=None):  # PREOPEN v85.178: at the seat, the chat is opened once - the digit later only fills the composer
    try:
        _d = re.sub(r'\D', '', str(phone))
        if len(_d) == 10:
            _d = '91' + _d
        if not _d:
            return False
        pw = _pw_fresh()  # PLAYWRIGHT-FRESH v85.185: a live instance or a new one, never a stopped one
        _door = pw.chromium.connect_over_cdp(_CDP_URL)
        _c = _door.contexts[0] if _door.contexts else _door.new_context()
        _pg = next((x for x in _c.pages if 'web.whatsapp.com' in (getattr(x, 'url', '') or '')), None)
        if _pg is None:
            return False
        if ('/send?phone=' + _d) in (_pg.url or ''):
            return True
        _arm_dialogs(_pg)  # DIALOG-ARM v85.179: a live draft must not block the seat from opening the chat
        _pg.goto('https://web.whatsapp.com/send?phone=' + _d, wait_until='domcontentloaded', timeout=20000)
        if say:
            say('   📱 chat pre-opened for +%s - the digit will only fill the text' % _d)
        return True
    except Exception:
        return False

def _send_review_body(phone, text, say=print, ask=None):  # LOOP-CLEAN v85.21  # POLICY-RESET v85.25  # QUIET-ASYNCIO v85.28  # WA-DIAG v85.28 (retired v85.29: the DIAG traceback proved the shadow silenced playwright's own heartbeat inside its fiber; the laws rest here as witnesses, their guards repinned)  # DRAFT-ONLY v85.150: the text is placed in the field and the ritual ends there - the send column belongs to the master alone
    digits = re.sub(r'\D', '', str(phone))
    if len(digits) == 10: digits = '91' + digits
    say(f"🌐 opening WhatsApp Web in the BUTLER window for +{digits}…")
    pw = _pw_fresh()  # PLAYWRIGHT-FRESH v85.185: a live instance or a new one, never a stopped one
    page = None
    browser = None  # the shared door is never queried as an owned browser
    _made = False  # KEEP-OPEN v85.182: did this call create the page, or borrow one?
    via_cdp = False
    try:
        try:
            _door = pw.chromium.connect_over_cdp(_CDP_URL)  # WARM-CLIENT v81.47 + v81.55: the shared door is never ours to query or close
            _ctx2 = _door.contexts[0] if _door.contexts else _door.new_context()
            _wa_pgs = [pg for pg in _ctx2.pages if 'web.whatsapp.com' in (getattr(pg, 'url', '') or '')]  # WARM-TAKE-OVER v85.174: the tab the house warmed is the door - seventeen tabs and a fresh load per press was the wound
            if _wa_pgs:
             page = _wa_pgs[0]  # SAME-TAB v85.193: one WhatsApp tab serves every deed - the master's drafts live in WhatsApp's own store, so navigating loses nothing
             _made = False  # KEEP-A-TAB v85.189: borrowed, never closed
             _made = False  # KEEP-OPEN v85.182: borrowed, never closed
             for _xp in _wa_pgs[1:]:  # WARM-TAKE-OVER v85.174: only the tabs this house opened are swept - the master's own stay
              try:
               if '/send?phone=' in (getattr(_xp, 'url', '') or ''): _xp.close()
              except Exception:
               pass
            else:
             page = (_ctx2.pages[0] if _ctx2.pages else _ctx2.new_page())  # WARM-TAKE-OVER v85.174: the context's own page before any new tab
             _made = not bool(_ctx2.pages)  # KEEP-OPEN v85.182: closing is for pages this house created
            via_cdp = True
        except Exception:
            ctx = _ctx()  # PERSISTENT-WA v84.38: reuse the living window instead of launching and closing one per draft
            page = ctx.pages[0] if ctx.pages else ctx.new_page()  # SAME-TAB v85.193: the fallback also keeps one page - WhatsApp holds the drafts  # FREE-TAB-BOTH v85.192 (retired v85.193: the master confirmed WhatsApp persists each draft itself)
            _made = not bool(ctx.pages)  # KEEP-OPEN v85.182: the living window is borrowed, not ours
            via_cdp = False
        _already = ('/send?phone=' + digits) in (page.url or '')  # PREOPEN v85.178: the seat already opened this chat - a digit must never reload it
        if _already:
         say('   ♻️ reusing the open chat - no reload')
        elif not _goto(page, f'https://web.whatsapp.com/send?phone={digits}', say):
         _np = _fresh_page(say)  # TARGET-RECOVER v85.219: a page closed under us gets one re-arm before any refusal
         if _np is not None:
          page = _np
          if not _goto(page, f'https://web.whatsapp.com/send?phone={digits}', say):
           say('⚠️ chat page did not load - scan QR in the opened window if asked, then retry')
         else:
          say('⚠️ chat page did not load - scan QR in the opened window if asked, then retry')
        if ('/send?phone=' + digits) not in (page.url or ''):  # SEE-FAILURE v85.183: a navigation that did not arrive is a fact, not a guess
         try:
          page.reload(wait_until='domcontentloaded', timeout=30000)
          _goto(page, f'https://web.whatsapp.com/send?phone={digits}', say)
         except Exception:
          pass
        if ('/send?phone=' + digits) not in (page.url or ''):
         say('⚠️ the window stayed on another chat - the draft will be parked, not placed')
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
        say('⏳ waiting for the composer - the window is loading, not hung')  # WAIT-SAY v85.45: a slow load reads as work in progress, never as a corpse
        try:  # EARLY-DOOR v81.92: ask WhatsApp within the first beats, not after the placement wait - poll for the modal or the field, whichever speaks first
            for _i in range(48):  # MODAL-WATCH v81.98: the door is asked until it answers - twenty-four beats, not four; the modal confesses, the composer releases, and only true ambiguity pays the full count
                if _no_wa_modal(page):
                    say('⚠️ WhatsApp says this number isn\'t on WhatsApp - nothing drafted; teach or re-pick a number that is registered')
                    LAST_FAIL[0] = 'dead'  # NOT-ON-WHATSAPP v81.90: WhatsApp's own visible words beat any guess
                    return False
                try:
                    if page.locator('footer div[contenteditable="true"]').count() > 0: break
                except Exception:
                    pass
                page.wait_for_timeout(500)
        except Exception:
            pass
        box = _composer_ready(page, timeout=30000)  # COMPOSER-WAIT v85.150: the field is waited for as a visible truth before any verdict is spoken
        if not box:
            say('⚠️ the message field never appeared - the window is not ready; nothing was typed, nothing was sent')
            return False
        ok_fill = _place_text(page, text, say)
        if not ok_fill:
            _notwa = _no_wa_modal(page)  # CONCISE v81.91: the paste advice is wrong when WhatsApp has already said there is no field
            if _notwa:
                say('⚠️ WhatsApp says this number isn\'t on WhatsApp - there is no message field to paste into; pick or teach a number that is registered')
                LAST_FAIL[0] = 'dead'
            if not _notwa: say('⚠️ field did not take the text automatically - paste the draft from above into the WhatsApp field yourself')
            return False
        LAST_FAIL[0] = ''
        say('📝 draft is in the WhatsApp field - NOT sent: review it and press Send yourself in the browser')  # DRAFT-ONLY v85.150: no Enter, no send button, no menu - the step simply ends and the chat returns
        return True  # ONE-KEY v84.46 (retired v85.150: no menu waits any more)  # FLUSH-CUE v85.14 (retired v85.150)  # NO-FIELD-EXIT v81.94 (retired v85.150: a dead number ends in one line, never a menu)
    except WaBusy:  # PROFILE-LOCK v85.150: a held profile climbs to the door that can name it
        LAST_FAIL[0] = 'lock'
        raise
    except Exception as e:
        say(f'⚠️ whatsapp failed: {e}')
        return False
    finally:
        try:
            if (not via_cdp) and page is not None and _made: page.close()  # KEEP-A-TAB v85.189: a page born into the warm browser stays - closing the last tab takes the whole door with it
        except Exception:
            pass
        try:
            pass  # NO-STOP v85.197: the driver serves the whole process - a second sync_playwright() start in one process is what raised "Sync API inside the asyncio loop"
        except Exception:
            pass


def send_review(phone, text, say=print, *a, **k):  # PLAYWRIGHT-THREAD v85.23 (retired v85.150)  # PLAYWRIGHT-PROCESS v85.24 (retired v85.150)  # WA-STATUS v85.31 (retired v85.150)  # DRIVER-GOODBYE v85.42 (retired v85.150: no node driver of ours outlives a call)  # HANG-CEILING v85.42 (retired v85.150: no child may hang, because no child is born)  # EPIPE-INPROC v85.150: the draft is placed in this very process - the child-process fallback is gone, so no pipe can close beneath it
    LAST_FAIL[0] = ''
    try:
        try:
         return bool(_send_review_body(phone, text, say))
        except KeyboardInterrupt:  # DIALOG-SAFE v85.206: a ^C at the window costs the send, never the chat
         say('⏸️ interrupted - nothing was sent; say retry when ready')
         return False
    except WaBusy as e:  # PROFILE-LOCK v85.150: the master's cure in one line, and the chat stays open
        LAST_FAIL[0] = 'lock'
        say(str(e))
        return False
    except Exception as e:
        _m = ('%r' % (e,)).lower()
        if 'epipe' in _m or 'has been closed' in _m:  # EPIPE-INPROC v85.150: a window that went away mid-draft is named, never raised
            say('🔌 the WhatsApp window closed mid-draft - open WhatsApp again and repeat; nothing was sent')
        else:
            say('⚠️ whatsapp failed: %s' % (e,))
    try:  # PARK-DRAFT v85.27: a broken window must never cost a courtesy - the exact draft parks by phone and names its own path
        pd = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drafts', 'parked')
        os.makedirs(pd, exist_ok=True)
        fn = os.path.join(pd, re.sub(r'\D', '', str(phone)) + '.txt')
        open(fn, 'w').write(text)
        say('📥 draft parked at ' + fn + ' - send it by hand or retry once the window is cured')
    except Exception:
        pass
    return False