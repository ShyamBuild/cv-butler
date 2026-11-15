import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
def perfile():
    S = {}
    for fn in ('butler.py', 'briefing.py', 'wa.py'):
        P = os.path.join(os.getcwd(), fn)
        S[fn] = set(markers(open(P).read().split('\n'))) if os.path.exists(P) else set()
    return S
M0 = perfile()
W0 = open('wa.py').read()
w = W0.split('\n')
snap = list(w)
b0 = next(k for k, l in enumerate(w) if l.startswith('def _send_review_body('))
q0 = next((k for k in range(b0, b0+14) if 'QUIET-ASYNCIO v85.28' in w[k]), None)
if q0 is not None:
    q1 = q0
    while q1 < len(w) and ('_a.' in w[q1] or '_no_running' in w[q1] or 'QUIET-ASYNCIO' in w[q1] or w[q1].strip().startswith('raise RuntimeError') or w[q1].strip().startswith('def _no_running')):
        q1 += 1
    del w[q0:q1]
    done.append('shadow-removed')
b0 = next(k for k, l in enumerate(w) if l.startswith('def _send_review_body('))
for k in range(b0, b0+12):
    if 'WA_DIAG' in w[k]:
        k2 = k
        while k2 < len(w) and (ind(w[k2]) >= ind(w[k]) or w[k2].strip() == ''):
            if w[k2].strip() == '' and k2+1 < len(w) and ind(w[k2+1]) < ind(w[k]): break
            k2 += 1
        del w[k:k2]
        done.append('diag-removed'); break
if 'def watest(' not in '\n'.join(w):
    i = next(k for k, l in enumerate(w) if l.startswith('def _send_review_body('))
    w[i:i] = ["def watest(say=print):  # WA-STEP v85.29: each door of the ritual opened in order and named aloud, with a QR pause the moment one is visible - the master's instinct, made a ladder",
              "    from playwright.sync_api import sync_playwright",
              "    say('1 start…')",
              "    pw = sync_playwright().start()",
              "    say('1 ok')",
              "    page = None",
              "    try:",
              "        say('2 cdp connect…')",
              "        d = pw.chromium.connect_over_cdp('http://127.0.0.1:9222')",
              "        page = (d.contexts[0] if d.contexts else d.new_context()).new_page()",
              "        say('2 ok - the shared warm door answered')",
              "    except Exception as e:",
              "        say('2 cdp refused: %r - opening the persistent BUTLER window' % (e,))",
              "        ctx = _ctx()",
              "        page = ctx.pages[0] if ctx.pages else ctx.new_page()",
              "        say('2 ok - persistent window opened')",
              "    try:",
              "        say('3 goto whatsapp…')",
              "        page.goto('https://web.whatsapp.com/', timeout=60000)",
              "        say('3 ok')",
              "    except Exception as e:",
              "        say('3 goto refused: %r' % (e,))",
              "        return False",
              "    html = page.content()",
              "    if 'Link your phone' in html or 'qr code' in html.lower():",
              "        say('🔐 QR visible - scan it now with your phone; the window stays open; press any key when linked')",
              "        _key('')",
              "        try:",
              "            page.reload(timeout=60000)",
              "        except Exception:",
              "            pass",
              "        html = page.content()",
              "    ok = ('conversation' in html) or ('chat' in html.lower()) or ('Link your phone' not in html and 'qr code' not in html.lower())",
              "    say('4 logged-in markers present: %s' % ok)",
              "    say('watest complete - the window stays open for the next send')",
              "    return bool(ok)",
              ""]
    done.append('watest-ladder')
srcw = '\n'.join(w)
if srcw != W0:
    ast.parse(srcw); open('wa.py', 'w').write(srcw)
M1 = perfile()
lost = set()
for fn in M0:
    lost |= (M0[fn] - M1.get(fn, set()))
if lost:
    print('⛔ witness diff per file:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff per file: 0 laws lost')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.29' not in t:
        open(AR, 'a').write('v85.29: the asyncio shadow and policy meddling removed (they silenced playwright\'s own heartbeat inside its fiber); wa.watest opens each ritual door in order, names refusals, and pauses for one QR scan when visible - the master\'s instinct made a ladder; S367 pins the shadow\'s absence (S367)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S367 no shadow may stand between playwright and its own heartbeat", "'S366 the ritual supplies its own quiet room whichever probe playwright consults", "ck('S367 no shadow may stand between playwright and its own heartbeat', ('_no_running' not in open(os.path.join(BASE_DIR, 'wa.py')).read()) and ('QUIET-ASYNCIO' not in open(os.path.join(BASE_DIR, 'wa.py')).read()) and ('def watest(' in open(os.path.join(BASE_DIR, 'wa.py')).read()))")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
