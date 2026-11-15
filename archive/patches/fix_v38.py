import ast
rep = {f: open(f).read().split('\n') for f in ('wa.py', 'butler.py')}
done, skipped = [], []
def P(L):
    try: ast.parse('\n'.join(L)); return True
    except Exception: return False
def ind(l): return len(l) - len(l.lstrip())
def edit(fn_, name, func):
    L = rep[fn_]
    try: L2 = func(list(L))
    except Exception: skipped.append(name + ':anchor'); return
    if not L2 or L2 == L: skipped.append(name + ':nochange'); return
    if not P(L2): skipped.append(name + ':syntax'); return
    rep[fn_] = L2; done.append(name)
BLOCK = ["say('🌐 opening WhatsApp Web in the BUTLER window - wait for the chat to load…')",
         "pw = sync_playwright().start()",
         "browser = None",
         "c2 = ''",
         "try:",
         "    browser = pw.chromium.launch_persistent_context(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wa_profile'), headless=False, no_viewport=True)",
         "    page = browser.pages[0] if browser.pages else browser.new_page()",
         "    if not _goto(page, f\"https://web.whatsapp.com/send?phone={digits}\"):",
         "        say('⚠️ chat page did not load - scan QR in the opened window if asked, then retry')",
         "        return False",
         "    box = None",
         "    for s in ('div[contenteditable=\"true\"][data-tab=\"10\"]', 'div[contenteditable=\"true\"][data-lexical-editor=\"true\"]', 'footer div[contenteditable=\"true\"]'):",
         "        try:",
         "            page.wait_for_selector(s, timeout=45000); box = page.locator(s).first; break",
         "        except Exception:",
         "            continue",
         "    if box is None:",
         "        say('⚠️ compose box not found in the butler window - retry once the chat is open')",
         "        return False",
         "    box.click()",
         "    page.keyboard.insert_text(text)",
         "    if os.path.exists(AUTOSEND):",
         "        sent = _click_send(page)",
         "        if sent: page.wait_for_timeout(1500)",
         "        say('✅ sent via WhatsApp Web (autosend)' if sent else '⚠️ send-button not found - click send yourself in the WA window')",
         "        return sent",
         "    say('📝 draft is now in the BUTLER window text field - review it THERE, click send yourself, then answer here:')",
         "    c2 = (ask or input)('   [Enter] I clicked send myself · [x] discard & clear: ').strip().lower()",
         "    if c2 == 'x':",
         "        try:",
         "            page.keyboard.press('Meta+A'); page.keyboard.press('Backspace')",
         "        except Exception:",
         "            pass",
         "        say('🗑 discarded - nothing sent')",
         "        return False",
         "    say('✅ sent (you clicked in WhatsApp)')",
         "    return True",
         "except Exception as e:",
         "    say(f'⚠️ whatsapp failed: {e}')",
         "    return False",
         "finally:",
         "    try:",
         "        if browser is not None: browser.close()",
         "    except Exception:",
         "        pass",
         "    try:",
         "        pw.stop()",
         "    except Exception:",
         "        pass"]
def w1(L):
    i = next(k for k, l in enumerate(L) if l.strip() == 'if os.path.exists(AUTOSEND):')
    d = ind(L[i])
    j = next(k for k in range(i, len(L)) if L[k].strip() == 'return True' and ind(L[k]) == d)
    L[i:j+1] = [d*' ' + x for x in BLOCK]
    return L
edit('wa.py', 'send-phase-restored', w1)
def s16(L):
    if "'S16 send phase launches+fills'" in '\n'.join(L): return L
    i = next(k for k, l in enumerate(L) if "'S15 autosend constant defined'" in l)
    d = ind(L[i])
    L.insert(i+1, d*' ' + "ck('S16 send phase launches+fills', 'launch_persistent_context' in _wa and 'keyboard.insert_text(text)' in _wa)")
    return L
edit('butler.py', 'S16-guard', s16)
for f in rep:
    open(f, 'w').write('\n'.join(rep[f]))
print('✅ applied:', done)
print('⏭ skipped:', skipped or 'none')
