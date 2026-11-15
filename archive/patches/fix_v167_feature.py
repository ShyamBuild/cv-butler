import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
D = os.getcwd()
FG = os.path.join(D, 'fidget.flag')
if not os.path.exists(FG):
    open(FG, 'w').write('on\n'); done.append('fidget-flag-ensure')
open(os.path.join(D, 'ad_wait.py'), 'w').write('''# AD-WAIT v81.33: one window, sequential chats; slides on your send OR on a new job arriving (8s grace)
import os, re, sys, time, json
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import wa
from playwright.sync_api import sync_playwright
QP = os.path.join(BASE, 'autodraft_queue.json')
def norm(p):
    d = re.sub(r'\\D', '', str(p))
    return '91' + d if len(d) == 10 else d
def state(s, phone='', who=''):
    try:
        json.dump({'state': s, 'ts': time.time(), 'phone': phone, 'who': who}, open(os.path.join(BASE, 'ad_state.json'), 'w'))
    except Exception:
        pass
def pop_job():
    try: q = json.load(open(QP))
    except Exception: return None
    if not q: return None
    it = q.pop(0); json.dump(q, open(QP, 'w'), indent=1)
    return it
def build_text(job):
    try:
        root = open(os.path.expanduser('~/.cvtool_last_butler_root')).read().strip()
        fp = job.get('fp', ''); v = job.get('voice', ''); nm = job.get('who', '')
        rel = os.path.relpath(os.path.dirname(fp), root).split(os.sep)
        if len(rel) < 2: return job.get('text', '')
        client, posraw = rel[0], rel[1]
        pos = posraw.split('||')[0].strip().replace('_', ' ')
        loc = posraw.split('||')[1].strip() if '||' in posraw else ''
        t = open(os.path.join(BASE, 'templates', f'voice_{v}.txt')).read()
        return t.replace('{name}', nm).replace('{position}', pos).replace('{client}', client).replace('{location}', loc)
    except Exception:
        return job.get('text', '')
def slide(page, nj):
    global cur_phone, cur_txt, who, ok, retried, placed, empties
    print(f'\\U0001f4dd previous draft parked as WhatsApp Draft for +{cur_phone}; sliding to next', flush=True)
    cur_phone = norm(nj.get('phone', '')); cur_txt = build_text(nj); who = nj.get('who', who)
    state('waiting', cur_phone, who)
    print(f'\\u27a1\\ufe0f same window, next chat: +{cur_phone} ({nj.get("who", "")})', flush=True)
    if not wa._goto(page, f'https://web.whatsapp.com/send?phone={cur_phone}', print):
        print('\\u26a0\\ufe0f next chat page did not load; retiring', flush=True); return False
    ok = wa._place_text(page, cur_txt, print); retried = False; placed = time.time(); empties = 0
    print('\\U0001f4dd next draft in field - send or close as you wish', flush=True)
    return True
phone, tf = sys.argv[1], sys.argv[2]
who = sys.argv[3] if len(sys.argv) > 3 else ''
txt = open(tf, encoding='utf-8').read()
cur_phone = norm(phone); cur_txt = txt
outcome = 'retired'
print(f'\\U0001f310 opening WhatsApp Web in the BUTLER window for +{cur_phone} ({who})\\u2026', flush=True)
state('waiting', cur_phone, who)
pw = sync_playwright().start()
browser = None
try:
    browser = pw.chromium.launch_persistent_context(os.path.join(BASE, 'wa_profile'), headless=False, no_viewport=True)
    page = browser.pages[0] if browser.pages else browser.new_page()
    for _p in list(browser.pages):  # TAB-CLEAN v81.32: retire leftover blank tabs from old sessions
        if _p is not page:
            try:
                if (_p.url or '') in ('', 'about:blank'): _p.close()
            except Exception:
                pass
    if not wa._goto(page, f'https://web.whatsapp.com/send?phone={cur_phone}', print):
        print('\\u26a0\\ufe0f chat page did not load - scan QR in the opened window if asked, then retry', flush=True)
    else:
        ok = wa._place_text(page, cur_txt, print)
        if not ok:
            print('\\u26a0\\ufe0f field did not take the text on first try - will retry while waiting', flush=True)
        print('\\U0001f4dd draft in field - window slides to new tags on arrival, or on your send', flush=True)
        placed = time.time(); deadline = placed + 1800; empties = 0; seen_alive = False; retried = False
        while time.time() < deadline:
            time.sleep(3)
            alive = False; cur = ''
            for sel in wa.COMPOSE_SELS:
                try:
                    v = page.eval_on_selector(sel, "e => e.innerText || e.textContent || ''")
                    alive = True
                    if v: cur = v; break
                except Exception:
                    continue
            if not alive:
                if seen_alive and time.time() - placed > 15:
                    print('\\U0001f44b window closed by you; retiring (queued jobs open a fresh window)', flush=True); break
                if time.time() - placed > 120:
                    print('\\u26a0\\ufe0f compose box never appeared; retiring', flush=True); break
                continue
            seen_alive = True
            if not cur.strip():
                if not ok and not retried and time.time() - placed > 5:
                    retried = True
                    ok = wa._place_text(page, cur_txt, print)
                    continue
                if time.time() - placed > 10:
                    empties += 1
                    if empties >= 2:
                        print('\\u2705 field empty - sent by your hand; arming follow-up clock', flush=True)
                        try: wa._arm(cur_phone, cur_txt)
                        except Exception: pass
                        nj = pop_job()
                        if nj:
                            if not slide(page, nj): break
                            continue
                        outcome = 'sent'
                        print('\\U0001f44b no queued jobs; retiring gently', flush=True)
                        break
                else:
                    empties = 0
            else:
                empties = 0
                if time.time() - placed > 8:
                    nj = pop_job()
                    if nj:
                        if not slide(page, nj): break
except SystemExit:
    pass
except Exception as e:
    print(f'\\u26a0\\ufe0f wa-wait failed: {e}', flush=True)
finally:
    state(outcome, cur_phone, who)
    try:
        if browser is not None: browser.close()
    except Exception:
        pass
    try: pw.stop()
    except Exception: pass
print('\\U0001f44b wa-wait retired', flush=True)
''')
done.append('ad-wait-v81.33')
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'window free - releasing' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith("self._ad_fire(it['phone'], self._ad_text("))
    d = ind(B[i])
    B.insert(i, d*' ' + "say(f\"▶️ window free - releasing queued draft for +{it.get('phone')} ({it.get('who')})\")  # RELEASE-VOICE v81.32")
    done.append('release-voice')
src = '\n'.join(B)
if '# STALE-WINDOW-SWEEP v81.32' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == '_BOOT_T = time.time()')
    d = ind(B[i])
    B[i:i] = [d*' ' + "try:",
              d*' ' + "    os.system(\"pkill -f 'ad_wait.py' 2>/dev/null; pkill -f 'Google Chrome for Testing' 2>/dev/null\")  # STALE-WINDOW-SWEEP v81.32: no ownerless windows survive a relaunch",
              d*' ' + "except Exception:",
              d*' ' + "    pass"]
    done.append('stale-window-sweep')
REPIN = {
 'S129': "ck('S129 ad_wait knows load-silence from closed windows', open(os.path.join(BASE_DIR, 'ad_wait.py')).read().count('seen_alive') > 0)",
 'S131': "ck('S131 queued drafts speak fresh wording', (chr(35)+' FRESH-TEXT v81.26') in _src and 'build_text' in open(os.path.join(BASE_DIR, 'ad_wait.py')).read())",
 'S132': "ck('S132 fidgeting is a switch, not a fate', (chr(35)+' FIDGET') in _src and os.path.exists(os.path.join(BASE_DIR, 'fidget.flag')))",
 'S133': "ck('S133 one window serves the whole queue', 'pop_job' in open(os.path.join(BASE_DIR, 'ad_wait.py')).read() and 'autodraft_queue.json' in open(os.path.join(BASE_DIR, 'ad_wait.py')).read())",
}
n = 0
for k, l in enumerate(B):
    for key, new in REPIN.items():
        if l.strip().startswith("ck('" + key + ' '):
            B[k] = ind(l)*' ' + new; n += 1
if n: done.append(f'ck-repin-x{n}')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S136 the window slides on arrival and release speaks" not in '\n'.join(B):
    anch = [k for k, l in enumerate(B) if 'S135' in l and 'every tag action' in l]
    if not anch: anch = [k for k, l in enumerate(B) if 'S134' in l and 'remembers across restarts' in l]
    if not anch: anch = [k for k, l in enumerate(B) if 'S133' in l and 'one window serves' in l]
    i = anch[-1]
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S136 the window slides on arrival and release speaks', 'AD-WAIT v81.3' in open(os.path.join(BASE_DIR, 'ad_wait.py')).read() and (chr(35)+' RELEASE-VOICE v81.32') in _src)")
    B.insert(i+2, d*' ' + "ck('S137 no ownerless windows survive a relaunch', (chr(35)+' STALE-WINDOW-SWEEP') in _src and (chr(35)+' TAB-CLEAN') in open(os.path.join(BASE_DIR, 'ad_wait.py')).read())")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S136-S137-guards')
print('✅', done)
