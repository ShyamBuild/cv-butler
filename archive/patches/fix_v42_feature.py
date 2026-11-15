import ast
rep = {f: open(f).read().split('\n') for f in ('briefing.py', 'wa.py', 'butler.py')}
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
FP = ["def do_fixphone(arg, root, say=print):",
      "    parts = (arg or '').split()",
      "    if len(parts) < 2: say('usage: fixphone <name or scan#> <10-digit phone>'); return",
      "    num = re.sub(r'\\D', '', parts[-1])",
      "    if len(num) == 10: num = '91' + num",
      "    who = ' '.join(parts[:-1])",
      "    path = None",
      "    if who.isdigit():",
      "        path = _scan_path(int(who), root)",
      "    else:",
      "        d0 = json.load(open(PHONES_FILE)) if os.path.exists(PHONES_FILE) else {}",
      "        c = [k for k in d0 if os.path.basename(k).lower().startswith(who.lower())]",
      "        if not c:",
      "            c = [os.path.join(dp, f) for dp, dn, fn in os.walk(root) for f in fn if f.lower().startswith(who.lower().rstrip('.'))][:1]",
      "        path = c[0] if c else None",
      "    if not path: say(f'no candidate for {who!r}'); return",
      "    d = json.load(open(PHONES_FILE)) if os.path.exists(PHONES_FILE) else {}",
      "    e = d.setdefault(path, {'k': '', 'phones': []})",
      "    e['phones'] = [num]",
      "    json.dump(d, open(PHONES_FILE, 'w'), indent=2)",
      "    say(f\"📞 learned: {os.path.basename(path)} -> +{num} (overrides PDF from now on)\")"]
def e1(L):
    if 'def do_fixphone(' in '\n'.join(L): return L
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def do_stale('))
    j = i + 1
    while j < len(L) and (not L[j].strip() or ind(L[j]) > 0): j += 1
    L[j:j] = FP + ['']
    return L
edit('briefing.py', 'fixphone-command', e1)
def e2(L):
    ch = False
    for k, l in enumerate(L):
        if "'brief','board','history','stale')" in l and 'fixphone' not in l:
            L[k] = l.replace("'stale')", "'stale','fixphone')"); ch = True; break
    for k, l in enumerate(L):
        if l.strip().startswith("elif cmd == 'stale'"):
            L.insert(k+1, ind(l)*' ' + "elif cmd == 'fixphone': do_fixphone(arg, root, print)"); ch = True; break
    for k, l in enumerate(L):
        if "startswith('stale')" in l and 'do_stale(q[' in l:
            L.insert(k+1, ind(l)*' ' + "if q.lower().startswith('fixphone '): do_fixphone(q[9:], root); continue"); ch = True; break
    return L if ch else L
edit('briefing.py', 'fixphone-routes', e2)
def e3(L):
    if "isn't on WhatsApp" in '\n'.join(L): return L
    i = next(k for k, l in enumerate(L) if 'ok_fill = _place_text(page, text, say)' in l)
    d = ind(L[i])
    L[i:i] = [d*' ' + 'try:',
              d*' ' + '    if "isn\'t on WhatsApp" in (page.content() or \'\'):',
              d*' ' + '        say(\'⚠️ WhatsApp says this number is not registered - nothing drafted. Correct it with: fixphone <name> <10-digit>\')',
              d*' ' + '        return False',
              d*' ' + 'except Exception:',
              d*' ' + '    pass']
    return L
edit('wa.py', 'wa-not-registered-detect', e3)
def e4(L):
    if '🔒 live lock' in '\n'.join(L): return L
    i = next(k for k, l in enumerate(L) if 'final-rules edition' in l)
    d = ind(L[i])
    L.insert(i+1, d*' ' + 'for _lf in sorted(__import__("glob").glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "butler_*.lock"))):')
    L.insert(i+2, (d+4)*' ' + 'try: print("   🔒 live lock: " + os.path.basename(_lf) + " -> " + open(_lf).read().strip())')
    L.insert(i+3, (d+4)*' ' + 'except Exception: pass')
    return L
edit('butler.py', 'lock-visibility', e4)
def e5(L):
    if "'S22 fixphone" in '\n'.join(L): return L
    i = next(k for k, l in enumerate(L) if "'S21 stage ageing" in l)
    d = ind(L[i])
    L.insert(i+1, d*' ' + "ck('S22 fixphone command routed', 'def do_fixphone(' in _br and \"cmd == 'fixphone'\" in _br)")
    L.insert(i+2, d*' ' + "ck('S23 not-on-WhatsApp aborts before gate', \"isn't on WhatsApp\" in _wa)")
    L.insert(i+3, d*' ' + "ck('S24 live locks visible at launch', '🔒 live lock: \" +' in _src)")
    return L
edit('butler.py', 'S22-S24-guards', e5)
for f in rep:
    open(f, 'w').write('\n'.join(rep[f]))
print('✅ applied:', done)
print('⏭ skipped:', skipped or 'none')
