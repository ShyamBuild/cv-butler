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
HELPER = ["COMPOSE_SELS = ('div[contenteditable=\"true\"][data-tab=\"10\"]', 'div[contenteditable=\"true\"][data-lexical-editor=\"true\"]', 'footer div[contenteditable=\"true\"]', 'div[contenteditable=\"true\"]')",
          'def _place_text(page, text, say=print):',
          '    for attempt in (0, 1, 2):',
          '        try:',
          '            box = None',
          '            for sel in COMPOSE_SELS:',
          '                try:',
          '                    page.wait_for_selector(sel, timeout=8000)',
          '                    box = sel; break',
          '                except Exception:',
          '                    continue',
          '            if not box: continue',
          '            page.click(box)',
          '            page.keyboard.insert_text(text)',
          '            page.wait_for_timeout(400)',
          "            got = page.eval_on_selector(box, \"e => e.innerText || e.textContent || ''\")",
          '            if got and got.strip() and text.split()[0].lower() in got.lower():',
          '                return True',
          '        except Exception:',
          '            pass',
          '        page.wait_for_timeout(1200)',
          '    return False',
          '']
def h1(L):
    if 'def _place_text(' in L: return L
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def send_review('))
    L[i:i] = HELPER
    return L
edit('wa.py', 'place-text-helper', h1)
NEW_BODY = ['def send_review(phone, text, say=print, ask=None):',
            "    digits = re.sub(r'\\D', '', str(phone))",
            "    if len(digits) == 10: digits = '91' + digits",
            "    say(f\"🌐 opening WhatsApp Web in the BUTLER window for +{digits}…\")",
            '    pw = sync_playwright().start()',
            '    browser = None',
            '    page = None',
            '    try:',
            "        browser = pw.chromium.launch_persistent_context(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wa_profile'), headless=False, no_viewport=True)",
            '        page = browser.pages[0] if browser.pages else browser.new_page()',
            "        if not _goto(page, f\"https://web.whatsapp.com/send?phone={digits}\", say):",
            "            say('⚠️ chat page did not load - scan QR in the opened window if asked, then retry')",
            '            return False',
            '        ok_fill = _place_text(page, text, say)',
            '        if not ok_fill:',
            "            say('⚠️ field did not take the text automatically - paste the draft from above into the WhatsApp field yourself, then:')",
            '        if os.path.exists(AUTOSEND):',
            '            sent = _click_send(page)',
            "            say('✅ sent via WhatsApp Web (autosend)' if sent else '⚠️ send-button not found - click send yourself in the WA window')",
            '            return bool(sent)',
            "        say('📝 message is in the WhatsApp text field - review it in the opened window, then:')",
            "        c = (ask or input)('   [Enter] I clicked send myself · [x] discard & clear: ').strip().lower()",
            "        if c == 'x':",
            '            try:',
            "                page.keyboard.press('Meta+A'); page.keyboard.press('Backspace')",
            '            except Exception:',
            '                pass',
            "            say('🗑 discarded - nothing sent')",
            '            return False',
            "        say('✅ sent (you clicked in WhatsApp)')",
            '        return True',
            '    except Exception as e:',
            "        say(f'⚠️ whatsapp failed: {e}')",
            '        return False',
            '    finally:',
            '        try:',
            '            if browser is not None: browser.close()',
            '        except Exception:',
            '            pass',
            '        try:',
            '            pw.stop()',
            '        except Exception:',
            '            pass',
            '']
def replace_body(L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def send_review('))
    d = ind(L[i])
    j = i + 1
    while j < len(L):
        s = L[j]
        if s.strip() and ind(s) <= d and (s.lstrip().startswith('def ') or s.lstrip().startswith('class ')): break
        j += 1
    L[i:j] = NEW_BODY
    return L
edit('wa.py', 'send-review-clean-rewrite', replace_body)
def s16(L):
    if "'S16 verified auto-fill" in '\n'.join(L): return L
    i = next(k for k, l in enumerate(L) if "'S15 autosend constant defined'" in l)
    d = ind(L[i])
    L.insert(i+1, d*' ' + "ck('S16 verified auto-fill', 'def _place_text(' in _wa and 'ok_fill = _place_text(page, text, say)' in _wa)")
    return L
edit('butler.py', 'S16-guard', s16)
for f in rep:
    open(f, 'w').write('\n'.join(rep[f]))
print('✅ applied:', done)
print('⏭ skipped:', skipped or 'none')
