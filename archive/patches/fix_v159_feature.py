import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
D = os.getcwd()
FG = os.path.join(D, 'fidget.flag')
if not os.path.exists(FG):
    open(FG, 'w').write('on\n'); done.append('fidget-flag')
open(os.path.join(D, 'ad_wait.py'), 'w').write('''# AD-WAIT v81.26: window waits for your thumb; state carries (file,tag) meta so butler marks the round done
import os, re, sys, time
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import wa
from playwright.sync_api import sync_playwright
phone, tf = sys.argv[1], sys.argv[2]
txt = open(tf, encoding='utf-8').read()
digits = re.sub(r'\\D', '', str(phone))
if len(digits) == 10: digits = '91' + digits
def state(s):
    try:
        import json as _j
        st = {'state': s, 'ts': time.time()}
        try: st['meta'] = _j.load(open(os.path.join(BASE, 'ad_meta.json')))
        except Exception: pass
        _j.dump(st, open(os.path.join(BASE, 'ad_state.json'), 'w'))
    except Exception:
        pass
print(f'\\U0001f310 opening WhatsApp Web in the BUTLER window for +{digits}\\u2026', flush=True)
state('waiting')
pw = sync_playwright().start()
browser = None
sent = False
try:
    browser = pw.chromium.launch_persistent_context(os.path.join(BASE, 'wa_profile'), headless=False, no_viewport=True)
    page = browser.pages[0] if browser.pages else browser.new_page()
    if not wa._goto(page, f'https://web.whatsapp.com/send?phone={digits}', print):
        print('\\u26a0\\ufe0f chat page did not load - scan QR in the opened window if asked, then retry', flush=True)
    else:
        try:
            if "isn't on WhatsApp" in (page.content() or ''):
                print('\\u26a0\\ufe0f number not registered - nothing drafted', flush=True)
                raise SystemExit(0)
        except SystemExit:
            raise
        except Exception:
            pass
        ok = wa._place_text(page, txt, print)
        if not ok:
            print('\\u26a0\\ufe0f field did not take the text on first try - will retry while waiting', flush=True)
        print('\\U0001f4dd draft in field - window STAYS open until you send (or 30 min idle)', flush=True)
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
                    print('\\U0001f44b window closed by you; retiring', flush=True); break
                if time.time() - placed > 120:
                    print('\\u26a0\\ufe0f compose box never appeared; retiring', flush=True); break
                continue
            seen_alive = True
            if not cur.strip():
                if not ok and not retried and time.time() - placed > 5:
                    retried = True
                    ok = wa._place_text(page, txt, print)
                    continue
                if time.time() - placed > 10:
                    empties += 1
                    if empties >= 2:
                        sent = True
                        print('\\u2705 field empty - sent by your hand; arming follow-up clock', flush=True)
                        try: wa._arm(digits, txt)
                        except Exception: pass
                        break
                else:
                    empties = 0
            else:
                empties = 0
except SystemExit:
    pass
except Exception as e:
    print(f'\\u26a0\\ufe0f wa-wait failed: {e}', flush=True)
finally:
    state('sent' if sent else 'retired')
    try:
        if browser is not None: browser.close()
    except Exception:
        pass
    try: pw.stop()
    except Exception: pass
print('\\U0001f44b wa-wait retired', flush=True)
''')
done.append('ad-wait-v81.26')
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# KIND v81.26' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == "if not hasattr(self, '_tagct'): self._tagct = {}")
    B.insert(i+1, ind(B[i])*' ' + "if not hasattr(self, '_tag_kind'): self._tag_kind = {}")
    c = next(k for k, l in enumerate(B) if '# CTIME-EYE v81.20' in l)
    j = next(k for k in range(c, c+30) if B[k].strip() == 'changed.append(fp)')
    B.insert(j+1, ind(B[j])*' ' + "self._tag_kind[fp] = 'set' if oldc != c else 'ctime'  # KIND v81.26")
    done.append('kind-classifier')
src = '\n'.join(B)
if '# FRESH-TEXT v81.26' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def _draft_one(self, fp, tg, v, mode, say'))
    d = ind(B[i])
    B[i] = d*' ' + "def _draft_one(self, fp, tg, v, mode, say, kind='set'):"
    B[i:i] = [d*' ' + "def _ad_text(self, fp, v, nm):  # FRESH-TEXT v81.26: queued drafts rebuild wording at fire time",
              d*' ' + "    try:",
              d*' ' + "        rel = os.path.relpath(os.path.dirname(fp), self.root).split(os.sep) if fp else []",
              d*' ' + "        if len(rel) < 2: return None",
              d*' ' + "        client, posraw = rel[0], rel[1]",
              d*' ' + "        pos = posraw.split('||')[0].strip().replace('_', ' ')",
              d*' ' + "        loc = posraw.split('||')[1].strip() if '||' in posraw else ''",
              d*' ' + "        t = open(os.path.join(BASE_DIR, 'templates', f'voice_{v}.txt')).read()",
              d*' ' + "        return t.replace('{name}', nm).replace('{position}', pos).replace('{client}', client).replace('{location}', loc)",
              d*' ' + "    except Exception:",
              d*' ' + "        return None",
              ""]
    k = next(k for k, l in enumerate(B) if l.strip() == 'if v: self._draft_one(fp, tg, v, mode, say)')
    B[k] = ind(B[k])*' ' + "if v: self._draft_one(fp, tg, v, mode, say, getattr(self, '_tag_kind', {}).get(fp, 'set'))"
    k = next(k for k, l in enumerate(B) if l.strip() == 'if time.time() - lg.get(k, 0) < 60: return')
    B.insert(k+1, ind(B[k])*' ' + "if kind == 'ctime' and not self._ad_fidget() and time.time() - lg.get(f'{fp}|{tg}', 0) < 21600: say(f'⏭️ autodraft: {os.path.basename(fp)} +{tg} already handled this round (sent or closed) - remove+add the tag to re-draft'); return  # DONE-MARK v81.26")
    k = next(k for k, l in enumerate(B) if l.strip() == "q.append({'phone': d, 'text': txt, 'at': time.time(), 'who': nm, 'voice': v})")
    B[k] = ind(B[k])*' ' + "q.append({'phone': d, 'text': txt, 'at': time.time(), 'who': nm, 'voice': v, 'fp': fp, 'tag': tg})"
    k = next(k for k, l in enumerate(B) if l.strip() == "q2.append({'phone': _d2, 'text': txt, 'at': time.time(), 'who': nm, 'voice': v})")
    B[k] = ind(B[k])*' ' + "q2.append({'phone': _d2, 'text': txt, 'at': time.time(), 'who': nm, 'voice': v, 'fp': fp, 'tag': tg})"
    k = next(k for k, l in enumerate(B) if l.strip() == "self._ad_fire(it['phone'], it['text'], it['voice'], it['who'], say)")
    B[k] = ind(B[k])*' ' + "self._ad_fire(it['phone'], self._ad_text(it.get('fp',''), it['voice'], it['who']) or it.get('text',''), it['voice'], it['who'], say, it.get('fp',''), it.get('tag',''))  # FRESH-TEXT v81.26"
    k = next(k for k, l in enumerate(B) if l.strip() == 'self._ad_fire(d, txt, v, nm, say)')
    B[k] = ind(B[k])*' ' + 'self._ad_fire(d, txt, v, nm, say, fp, tg)'
    k = next(k for k, l in enumerate(B) if l.strip().startswith('def _ad_fire(self, d, txt, v, nm, say):'))
    B[k] = ind(B[k])*' ' + "def _ad_fire(self, d, txt, v, nm, say, fp='', tg=''):  # AD-FIRE v81.5 (subprocess: playwright needs a main thread)"
    k = next(k for k, l in enumerate(B) if 'ad_wait.py' in l and 'Popen' in l)
    B.insert(k, ind(B[k])*' ' + "try: json.dump({'fp': fp, 'tag': tg, 'phone': d, 'voice': v}, open(os.path.join(BASE_DIR, 'ad_meta.json'), 'w'))")
    B.insert(k+1, ind(B[k])*' ' + "except Exception: pass")
    done.append('fire-meta')
src = '\n'.join(B)
if '# FIDGET v81.27' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def _ad_busy(self):'))
    d = ind(B[i])
    B[i:i] = [d*' ' + "def _ad_fidget(self):  # FIDGET v81.27: testing switch - filesystem fidgeting re-drafts on demand",
              d*' ' + "    try: return open(os.path.join(BASE_DIR, 'fidget.flag')).read().strip() == 'on'",
              d*' ' + "    except Exception: return False",
              ""]
    done.append('fidget-switch')
if "'_ad_done_seen'" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.strip() == "qp = os.path.join(BASE_DIR, 'autodraft_queue.json')" and ind(l) == 12)
    d = ind(B[i])
    B[i:i] = [d*' ' + "try: stt = json.load(open(os.path.join(BASE_DIR, 'ad_state.json')))",
              d*' ' + "except Exception: stt = {}",
              d*' ' + "if stt.get('state') in ('sent', 'retired') and stt.get('meta') and getattr(self, '_ad_done_seen', 0) != stt.get('ts'):",
              d*' ' + "    self._ad_done_seen = stt.get('ts')",
              d*' ' + "    m = stt['meta']",
              d*' ' + "    lp2 = os.path.join(BASE_DIR, 'autodraft_log.json')",
              d*' ' + "    try: lg2 = json.load(open(lp2))",
              d*' ' + "    except Exception: lg2 = {}",
              d*' ' + "    lg2[str(m.get('fp')) + '|' + str(m.get('tag'))] = time.time()",
              d*' ' + "    json.dump(lg2, open(lp2, 'w'), indent=1)",
              d*' ' + "    say('📬 draft round closed (' + str(stt.get('state')) + ') for ' + str(m.get('tag')) + ' - noted done this round')  # DONE-MARK v81.26"]
    done.append('done-mark-tick')
src = '\n'.join(B)
for k, l in enumerate(B):
    if "'S129 ad_wait knows load-silence from closed windows" in l:
        B[k] = ind(l)*' ' + "ck('S129 ad_wait knows load-silence from closed windows', 'AD-WAIT v81.2' in open(os.path.join(BASE_DIR, 'ad_wait.py')).read() and 'seen_alive' in open(os.path.join(BASE_DIR, 'ad_wait.py')).read())"
        done.append('S129-repin'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S130 closed or sent marks the round done" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S129 ad_wait knows load-silence from closed windows" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S130 closed or sent marks the round done', (chr(35)+' DONE-MARK v81.26') in _src and (chr(35)+' KIND v81.26') in _src)")
    B.insert(i+2, d*' ' + "ck('S131 queued drafts speak fresh wording', (chr(35)+' FRESH-TEXT v81.26') in _src and 'AD-WAIT v81.2' in open(os.path.join(BASE_DIR, 'ad_wait.py')).read())")
    B.insert(i+3, d*' ' + "ck('S132 fidgeting is a switch, not a fate', (chr(35)+' FIDGET v81.27') in _src and os.path.exists(os.path.join(BASE_DIR, 'fidget.flag')))")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S130-S132-guards')
print('✅', done)
