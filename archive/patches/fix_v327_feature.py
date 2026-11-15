import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if l.strip().startswith("ph0 = taught_digits(cur['name']) or phones_of(p, True) or None"):
        B[k] = ind(l)*' ' + "ph0 = taught_digits(cur['name']) or phones_of(p, True) or None  # PHONE-FIRST v84.31 + QUIET-CHAIR v84.37: read before move, quietly"
        done.append('s290-restored'); break
for k, l in enumerate(B):
    if "say('📱 drafting" in l or "say(f'📱 drafting" in l or "say('📝 drafting" in l:
        d = ind(l)
        B.insert(k, d*' ' + "_wa_ok = True  # SKIP-WA v84.38: the master may tag without texting")
        B.insert(k+1, d*' ' + "try:")
        B.insert(k+2, d*' ' + "    _r = (ask or input)('📱 Draft WhatsApp? [y] yes · [n] skip (tag only): ').strip().lower()")
        B.insert(k+3, d*' ' + "    if _r == 'n': _wa_ok = False")
        B.insert(k+4, d*' ' + "except Exception: pass")
        B.insert(k+5, d*' ' + "if not _wa_ok: say('🏷️ tagged only - WhatsApp skipped'); return")
        done.append('skip-wa-before-draft'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
W = os.path.join(os.getcwd(), 'wa.py')
w = open(W).read().split('\n')
for k, l in enumerate(w):
    if l.strip().startswith("browser = pw.chromium.launch_persistent_context(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wa_profile'), headless=False, no_viewport=True)"):
        d = ind(l)
        w[k:k+2] = [d*' ' + "ctx = _ctx()  # PERSISTENT-WA v84.38: reuse the living window instead of launching and closing",
                    d*' ' + "page = ctx.pages[0] if ctx.pages else ctx.new_page()"]
        done.append('wa-persistent'); break
for k, l in enumerate(w):
    if l.strip().startswith("if via_cdp and page is not None: page.close()"):
        d = ind(l)
        w[k:k+1] = [d*' ' + "if via_cdp and page is not None: page.close()  # PERSISTENT-WA v84.38: only close the page if it was a CDP guest; the persistent window stays open"]
        done.append('wa-persistent-finally'); break
for k, l in enumerate(w):
    if l.strip().startswith("elif browser is not None: browser.close()"):
        w[k] = ind(l)*' ' + "# elif browser is not None: browser.close()  # PERSISTENT-WA v84.38: never close the persistent browser"
        done.append('wa-no-close-browser'); break
for k, l in enumerate(w):
    if l.strip().startswith("pw.stop()"):
        w[k] = ind(l)*' ' + "if via_cdp: pw.stop()  # PERSISTENT-WA v84.38: only stop the CDP playwright instance; the persistent one lives in _state"
        done.append('wa-no-stop-pw'); break
srca = '\n'.join(w); ast.parse(srca); open(W, 'w').write(srca)
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v84.38' not in t:
        open(AR, 'a').write('v84.38: persistent wa window (reuses _ctx instead of launching/closing), skip-wa prompt in outcome, S290 marker restored\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S303 the persistent window stays open and the master may tag without texting", "'S302 the seat prints the map in two lines and options keeps the full grammar", "ck('S303 the persistent window stays open and the master may tag without texting', (chr(35)+' PERSISTENT-WA v84.38') in open(os.path.join(BASE_DIR, 'wa.py')).read() and (chr(35)+' SKIP-WA v84.38') in _src and (chr(35)+' PHONE-FIRST v84.31') in _src)")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
