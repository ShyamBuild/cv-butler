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
NEW = ["if os.path.exists(AUTOSEND):",
       "    sent = _click_send(page)",
       "    if sent: page.wait_for_timeout(1500)",
       "    say(\"✅ sent via WhatsApp Web (autosend)\" if sent else \"⚠️ send-button not found - click send yourself in the WA window\")",
       "    return sent",
       "say(\"📝 message is in the WhatsApp text field - review it in the opened window, then:\")",
       "c = (ask or input)(\"   [Enter] I clicked send myself · [x] discard & clear · [q] leave in field & close: \").strip().lower()",
       "if c == 'x':",
       "    try:",
       "        page.keyboard.press('Meta+A'); page.keyboard.press('Backspace')",
       "    except Exception:",
       "        pass",
       "    say(\"🗑 discarded - nothing sent\")",
       "    return False",
       "if c == 'q':",
       "    say(\"📝 left in the WhatsApp text field - send when ready\")",
       "    return False",
       "say(\"✅ sent (you clicked in WhatsApp)\")",
       "return True"]
def w1(L):
    i = next(k for k, l in enumerate(L) if l.strip() == "if c == '':")
    d = ind(L[i])
    j = i + 1
    while j < len(L) and not (L[j].strip() == 'return sent' and ind(L[j]) == d):
        j += 1
    L[i:j+1] = [d*' ' + x for x in NEW]
    return L
edit('wa.py', 'manual-send-default', w1)
edit('wa.py', 'hint-updated', lambda L: [l.replace('type Enter to send · e edit · n number · q skip', 'Enter = I sent it myself · x discard · q leave in field · e edit · n number') for l in L])
def s14(L):
    if "'S14 manual-send default'" in '\n'.join(L): return L
    i = next(k for k, l in enumerate(L) if "'S13 missed phone-first" in l)
    d = ind(L[i])
    L.insert(i+1, d*' ' + "ck('S14 manual-send default', 'I clicked send myself' in _wa)")
    return L
edit('butler.py', 'S14-guard', s14)
for f in rep:
    open(f, 'w').write('\n'.join(rep[f]))
print('✅ applied:', done)
print('⏭ skipped:', skipped or 'none')
