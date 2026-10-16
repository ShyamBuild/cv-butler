import os, re, json, time
BASE = os.path.dirname(os.path.abspath(__file__))
CONV = os.path.join(BASE, 'conversations.json')
def _load():
    try: return json.load(open(CONV))
    except Exception: return {}
def _save(d):
    t = CONV + '.tmp'; json.dump(d, open(t, 'w'), indent=2); os.replace(t, CONV)
def open_loops():
    phones = []
    try:
        ob = json.load(open(os.path.join(BASE, 'outbox.json')))
        for i in ob.get('items', []):
            if not i.get('done') and i.get('phone'): phones.append(i['phone'])
    except Exception: pass
    try:
        cs = json.load(open(os.path.join(BASE, 'cases.json')))
        for k, c in cs.items():
            if c.get('last_contact') and time.time() - c['last_contact'] < 14 * 86400 and c.get('phones'):
                phones += c['phones']
    except Exception: pass
    out = []
    for p in phones:
        d = re.sub(r'\D', '', str(p))
        if d and d not in out: out.append(d)
    return out[:12]
def recap(say=print, show=False):
    loops = open_loops()
    if not loops: say('📭 no open loops with phones - nothing to read'); return
    from playwright.sync_api import sync_playwright
    say(f'📖 reading {len(loops)} open-loop chat(s), read-only (never run during a send)…')
    pw = sync_playwright().start(); browser = None; d = _load()
    try:
        browser = pw.chromium.launch_persistent_context(os.path.join(BASE, 'wa_profile'), headless=not show, no_viewport=True)
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto('https://web.whatsapp.com', timeout=90000, wait_until='domcontentloaded')
        logged = False
        for _ in range(60):
            if page.locator('div[data-testid="chat-list"]').count(): logged = True; break
            time.sleep(2)
        if not logged:
            say('⚠️ not logged in headless - run once with a window: recap show'); return
        for ph in loops:
            try:
                page.goto(f'https://web.whatsapp.com/send?phone={ph}', timeout=60000, wait_until='domcontentloaded')
                for _ in range(30):
                    if page.locator('div[data-testid="conversation-panel-wrapper"]').count(): break
                    time.sleep(2)
                bubbles = page.locator('div[data-testid="conversation-panel-wrapper"] div[data-id]')
                n = bubbles.count(); msgs = []
                for i in range(max(0, n - 25), n):
                    b = bubbles.nth(i)
                    mine = b.evaluate("e => e.classList.contains('message-out')")
                    txt = (b.inner_text() or '').strip().split('\n')
                    msgs.append({'dir': 'out' if mine else 'in', 'text': (txt[0] if txt else '')[:300], 'at': int(time.time())})
                if msgs:
                    d[ph] = {'read_at': int(time.time()), 'messages': msgs[-25:]}
                    li = next((m for m in reversed(msgs) if m['dir'] == 'in'), None)
                    say(f'   {ph}: {len(msgs)} msg(s)' + (f' · last inbound: "{li["text"][:60]}"' if li else ' · no inbound yet'))
                else:
                    say(f'   {ph}: chat open, no readable bubbles')
            except Exception as e:
                say(f'   {ph}: skip ({str(e)[:60]})')
        _save(d)
        try:
            ob = json.load(open(os.path.join(BASE, 'outbox.json')))
            for i in ob.get('items', []):
                if i.get('kind') == 'ack_check' and not i.get('done') and re.sub(r'\D', '', str(i.get('phone') or '')) in d:
                    if any(m['dir'] == 'in' for m in d[re.sub(r'\D', '', str(i['phone']))]['messages'][-5:]):
                        say(f'   💬 inbound seen for {i.get("name") or i["phone"]} - close the loop: ack {i.get("name") or i["phone"]}')
        except Exception: pass
    finally:
        try:
            if browser is not None: browser.close()
        except Exception: pass
        try: pw.stop()
        except Exception: pass
    say('✅ recap stored in conversations.json (read-only: no clicks, no sends)')
def last_inbound(phone, say=print):
    d = _load(); ph = re.sub(r'\D', '', str(phone))
    e = d.get(ph)
    if not e: say('no recap for this number yet - run: recap'); return None
    li = next((m for m in reversed(e['messages']) if m['dir'] == 'in'), None)
    if li: say(f'📨 last inbound: {li["text"]}')
    else: say('no inbound captured yet')
    return li
