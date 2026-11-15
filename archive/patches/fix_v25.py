import ast
rep = {f: open(f).read().split('\n') for f in ('butler.py', 'briefing.py', 'wa.py')}
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
def cut0(L, i):
    d = ind(L[i]); j = i + 1
    while j < len(L):
        s = L[j]
        if s.strip() and ind(s) <= d and (s.lstrip().startswith('def ') or s.lstrip().startswith('class ')): break
        j += 1
    return j
def ins_after(L, pred, lines):
    i = next(k for k, l in enumerate(L) if pred(l))
    L[i+1:i+1] = lines; return L
def repl(L, old, new):
    return [new if l.strip() == old else l for l in L]

edit('butler.py', 'interactive-flag', lambda L: ins_after(L, lambda l: l.strip().startswith('VERSION ='), ['INTERACTIVE = False']) if 'INTERACTIVE = False' not in L else L)
def b2(L):
    i = next(k for k, l in enumerate(L) if '[rename] failed: {ob}' in l)
    d = ind(L[i-1])
    L[i-1:i-1] = [d*' ' + 'except FileNotFoundError:', d*' ' + '    log.info(f"file disappeared before rename: {ob}")', d*' ' + '    return']
    return L
edit('butler.py', 'rename-vanished-quiet', b2)
edit('butler.py', 'idx-helper', lambda L: ins_after(L, lambda l: l.strip().startswith('LOCK_FILE ='), ['def _idx_path(root):', '    import hashlib', "    return os.path.join(BASE_DIR, 'scan_index_' + hashlib.md5(os.path.abspath(root).encode()).hexdigest()[:8] + '.json')", '']) if 'def _idx_path(root):' not in L else L)
edit('butler.py', 'save-idx-per-root', lambda L: repl(L, "open(os.path.join(BASE_DIR, 'scan_index.json'), 'w'))", "open(_idx_path(self.root), 'w'))") if any('scan_index.json' in l and 'idx' in l for l in L) else None)
def b5(L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('print(f"💓 sweep #{n}'))
    d = ind(L[i])
    j = i + 1
    while j < len(L) and ('_reconcile_tags' in L[j] or 'reconcile error' in L[j] or L[j].strip() in ('except Exception: pass', 'except Exception as _re: pass')):
        j += 1
    blk = [d*' ' + 'if not INTERACTIVE:', d*' ' + '    ' + L[i].strip(), d*' ' + 'def hsay(m):', d*' ' + '    if INTERACTIVE: log.info(m)', d*' ' + '    else: print(m)']
    for k in range(i+1, j):
        blk.append(d*' ' + '    ' + L[k].strip().replace('(print)', '(hsay)'))
    L[i:j] = blk; return L
edit('butler.py', 'sweeps-silenced', b5)
def b7(L):
    i = next(k for k, l in enumerate(L) if l.strip() == 'try: raw = tty.readline().strip(); line = raw.lower()')
    d = ind(L[i])
    L[i:i+1] = [d*' ' + 'try:', d*' ' + '    INTERACTIVE = True', d*' ' + '    raw = tty.readline().strip(); line = raw.lower()', d*' ' + 'finally:', d*' ' + '    INTERACTIVE = False']
    return L
edit('butler.py', 'console-read-flagged', b7)
def b8(L):
    i = next(k for k, l in enumerate(L) if l.strip() == 'def _ask(prompt):')
    d = ind(L[i])
    L[i+1:i+3] = [d*' ' + '    global INTERACTIVE', d*' ' + '    print(prompt, end=\'\', flush=True)', d*' ' + '    INTERACTIVE = True', d*' ' + '    try: return tty.readline().strip()', d*' ' + '    finally: INTERACTIVE = False']
    return L
edit('butler.py', 'ask-flagged', b8)

edit('briefing.py', 'briefing-helpers', lambda L: ins_after(L, lambda l: l.strip().startswith('def _scan_path('), ['def _phone_first(arg):', "    m = re.match(r'^\\s*(\\d{10}|\\d{12})\\b\\s*(.*)$', arg or '', re.S)", '    if not m: return None, arg', '    d = m.group(1)', "    if len(d) == 10: d = '91' + d", '    return d, m.group(2).strip()', '']) if 'def _phone_first' not in L else L)
def f3(L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def _scan_path('))
    L[i:cut0(L, i)] = ['def _scan_path(num, root=None):', '    cands = []', '    if root: cands.append(_idx_path(root))', "    cands.append(os.path.join(BASE_DIR, 'scan_index.json'))", '    for c in cands:', '        try:', '            d = json.load(open(c))', "            if root and d.get('root') and os.path.abspath(d['root']) != os.path.abspath(root): continue", "            p = d.get('idx', {}).get(str(num))", '            if p and os.path.exists(p): return p', '        except Exception:', '            pass', '    return None', '']
    return L
edit('briefing.py', 'scan-path-per-root', f3)
edit('briefing.py', 'idx-helper-b', lambda L: ins_after(L, lambda l: l.strip().startswith('TAGS_CACHE ='), ['def _idx_path(root):', '    import hashlib', "    return os.path.join(BASE_DIR, 'scan_index_' + hashlib.md5(os.path.abspath(root).encode()).hexdigest()[:8] + '.json')", '']) if 'def _idx_path' not in L else L)
def f4(L):
    for a, b in (('_scan_path(arg.strip())', '_scan_path(arg.strip(), root)'), ('_scan_path(toks[0])', '_scan_path(toks[0], root)'), ('_scan_path(q.strip())', '_scan_path(q.strip(), root)')):
        L = [l.replace(a, b) for l in L]
    return L
edit('briefing.py', 'scan-callers-root', f4)
edit('briefing.py', 'do-list-per-root', lambda L: [l.replace("open(os.path.join(BASE_DIR, 'scan_index.json'), 'w')", 'open(_idx_path(root), \'w\')') if 'json.dump' in l or 'scan_index' in l else l for l in L])
def phone_block(tpl_expr):
    return ['    ph0, rest0 = _phone_first(arg)', '    if ph0:', "        nm = rest0.title() or 'there'", "        pos = f['display'] if f else clean_pos(os.path.basename(root))", "        cli = f['client'] if f else re.sub(r'^\\d+[\\s_-]*', '', os.path.basename(os.path.dirname(root)))", '        tpl = ' + tpl_expr, '        try: text = tpl.format(name=nm, position=pos, company=cli)', '        except Exception: text = tpl', '        try:', '            import wa', '            wa.send_review(ph0, text, say, ask=ask)', '        except Exception as e:', '            say(f"⚠️ whatsapp failed: {e}")', '        return']
def mk(fnname, tpl):
    def f(L):
        i = next(k for k, l in enumerate(L) if l.strip().startswith('def ' + fnname + '('))
        j = next(k for k in range(i+1, len(L)) if L[k].strip().startswith('hit = _scan_path'))
        L[j:j] = phone_block(tpl)
        return L
    return f
edit('briefing.py', 'do-send-phone-first', mk('do_send', "_tpl_for(tpl_words)"))
edit('briefing.py', 'do-missed-phone-first', mk('do_missed', "_tpl_for(['missed'])"))

edit('wa.py', 'wa-goto-helper', lambda L: ins_after(L, lambda l: l.strip().startswith('def _click_send(') and False or l.strip().startswith('def send_review('), ['def _goto(page, url, say=print):', '    for a in (0, 1):', '        try:', "            page.goto(url, timeout=90000, wait_until='domcontentloaded'); return True", '        except Exception:', '            if a == 0: time.sleep(2)', "    say('⚠️ WhatsApp page did not load (network?) - try again in a minute')", '    return False', '']) if 'def _goto(' not in L else L)
edit('wa.py', 'wa-goto-used', lambda L: [l.replace('page.goto("https://web.whatsapp.com")', '_goto(page, "https://web.whatsapp.com")').replace('page.goto(f"https://web.whatsapp.com/send?phone={digits}")', 'if not _goto(page, f"https://web.whatsapp.com/send?phone={digits}"): return False') for l in L])
def w3(L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith("for sel in ('button[data-testid=\"compose-btn-send\"]', 'span[data-icon=\"btn-send\"]'):"))
    d = ind(L[i])
    L[i-1:i+4] = [d*' ' + 'sent = _click_send(page)']
    return L
edit('wa.py', 'wa-interactive-click-send', w3)
def w4(L):
    i = next(k for k, l in enumerate(L) if l.strip() == "if c == '':")
    d = ind(L[i]); j = i + 1
    while j < len(L) and (not L[j].strip() or ind(L[j]) > d): j += 1
    L[j:j] = [d*' ' + 'say("   (type Enter to send · e edit · n number · q skip)")']
    return L
edit('wa.py', 'wa-invalid-hint', w4)

def s1(L):
    i = next(k for k, l in enumerate(L) if "'S6 watcher handler intact'" in l)
    dd = ind(L[i])
    L[i+1:i+1] = [dd*' ' + "_wa = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wa.py')).read()",
                  dd*' ' + "_br = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'briefing.py')).read()",
                  dd*' ' + "ck('S7 wa interactive uses _click_send', 'sent = _click_send(page)' in _wa)",
                  dd*' ' + "ck('S8 scan index per-root', 'def _scan_path(num, root=None)' in _br)",
                  dd*' ' + "ck('S9 rename swallows vanished files', 'except FileNotFoundError:' in _src)",
                  dd*' ' + "ck('S10 prompts silence sweeps', 'INTERACTIVE = False' in _src)"]
    return L
if "'S7 wa interactive" not in '\n'.join(rep['butler.py']):
    edit('butler.py', 'selftest-S7-S10', s1)
for f in rep:
    open(f, 'w').write('\n'.join(rep[f]))
print('✅ applied:', done)
print('⏭ skipped:', skipped or 'none')
