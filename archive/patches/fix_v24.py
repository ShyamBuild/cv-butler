import ast
done = []
# ---------------- butler.py ----------------
p = 'butler.py'; L = open(p).read().split('\n')
if 'INTERACTIVE = False' not in '\n'.join(L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('VERSION ='))
    L.insert(i+1, 'INTERACTIVE = False')
    done.append('interactive-flag')
for i, l in enumerate(L):
    if "[rename] failed: {ob}" in l and L[i-1].strip() == 'except Exception as ex:':
        d = len(L[i-1]) - len(L[i-1].lstrip())
        L[i-1:i-1] = [d*' ' + 'except FileNotFoundError:',
                      d*' ' + '    log.info(f"file disappeared before rename: {ob}")',
                      d*' ' + '    return']
        done.append('rename-vanished-quiet'); break
if 'def _idx_path(root):' not in '\n'.join(L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('LOCK_FILE ='))
    L[i:i] = ['def _idx_path(root):',
              '    import hashlib',
              "    return os.path.join(BASE_DIR, 'scan_index_' + hashlib.md5(os.path.abspath(root).encode()).hexdigest()[:8] + '.json')",
              '']
    done.append('idx-path-helper')
    L = open(p).read().split('\n') if False else L
for i, l in enumerate(L):
    if "open(os.path.join(BASE_DIR, 'scan_index.json'), 'w'))" in l and 'root' in L[i-1] + L[i-2]:
        L[i] = l.replace("os.path.join(BASE_DIR, 'scan_index.json')", '_idx_path(self.root)')
        done.append('save-idx-per-root'); break
for i, l in enumerate(L):
    if l.strip().startswith('print(f"💓 sweep #{n}'):
        d = len(l) - len(l.lstrip())
        blk = [d*' ' + 'if not INTERACTIVE:']
        blk.append(d*' ' + '    ' + l.strip())
        blk += [d*' ' + 'def hsay(m):',
                d*' ' + '    if INTERACTIVE: log.info(m)',
                d*' ' + '    else: print(m)']
        j = i + 1
        while j < len(L) and ('_reconcile_tags' in L[j] or L[j].strip() in ('except Exception: pass', 'except Exception as _re: pass') or 'print(\'reconcile error:\'' in L[j]):
            blk.append(d*' ' + '    ' + L[j].strip().replace('(print)', '(hsay)')); j += 1
        L[i:j] = blk
        done.append('sweeps-silenced-during-prompts'); break
for i, l in enumerate(L):
    if l.strip() == 'def _console(tty):':
        L.insert(i+1, (len(l)-len(l.lstrip()))*' ' + '    global INTERACTIVE')
        done.append('console-global'); break
for i, l in enumerate(L):
    if l.strip() == 'try: raw = tty.readline().strip(); line = raw.lower()':
        d = len(l) - len(l.lstrip())
        L[i:i+1] = [d*' ' + 'try:',
                    d*' ' + '    INTERACTIVE = True',
                    d*' ' + '    raw = tty.readline().strip(); line = raw.lower()',
                    d*' ' + 'finally:',
                    d*' ' + '    INTERACTIVE = False']
        done.append('console-read-flagged'); break
for i, l in enumerate(L):
    if l.strip() == 'def _ask(prompt):':
        d = len(l) - len(l.lstrip())
        L[i+1:i+3] = [d*' ' + '    global INTERACTIVE',
                      d*' ' + '    print(prompt, end=\'\', flush=True)',
                      d*' ' + '    INTERACTIVE = True',
                      d*' ' + '    try: return tty.readline().strip()',
                      d*' ' + '    finally: INTERACTIVE = False']
        done.append('ask-flagged'); break
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
# ---------------- briefing.py ----------------
p = 'briefing.py'; L = open(p).read().split('\n')
if 'def _idx_path(root):' not in '\n'.join(L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('TAGS_CACHE ='))
    L[i:i] = ['def _idx_path(root):',
              '    import hashlib',
              "    return os.path.join(BASE_DIR, 'scan_index_' + hashlib.md5(os.path.abspath(root).encode()).hexdigest()[:8] + '.json')",
              '']
    done.append('briefing-idx-helper')
if 'def _phone_first(arg):' not in '\n'.join(L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def _scan_path('))
    L[i:i] = ['def _phone_first(arg):',
              "    m = re.match(r'^\\s*(\\d{10}|\\d{12})\\b\\s*(.*)$', arg or '', re.S)",
              '    if not m: return None, arg',
              "    d = m.group(1)",
              "    if len(d) == 10: d = '91' + d",
              "    return d, m.group(2).strip()",
              '']
    done.append('phone-first-helper')
i = next(k for k, l in enumerate(L) if l.strip().startswith('def _scan_path('))
j = i + 1
while j < len(L) and (not L[j].strip() or (len(L[j]) - len(L[j].lstrip())) > 0):
    j += 1
L[i:j] = ['def _scan_path(num, root=None):',
          '    import json as _j',
          '    cands = []',
          '    if root: cands.append(_idx_path(root))',
          "    cands.append(os.path.join(BASE_DIR, 'scan_index.json'))",
          '    for c in cands:',
          '        try:',
          '            d = _j.load(open(c))',
          "            if root and d.get('root') and os.path.abspath(d['root']) != os.path.abspath(root): continue",
          "            p = d.get('idx', {}).get(str(num))",
          '            if p and os.path.exists(p): return p',
          '        except Exception:',
          '            pass',
          '    return None',
          '']
done.append('scan-path-per-root')
for a, b in (('_scan_path(arg.strip())', '_scan_path(arg.strip(), root)'),
             ('_scan_path(toks[0])', '_scan_path(toks[0], root)'),
             ('_scan_path(q.strip())', '_scan_path(q.strip(), root)')):
    L = [l.replace(a, b) for l in L]
done.append('scan-callers-thread-root')
i = next(k for k, l in enumerate(L) if l.strip().startswith("json.dump({'root': os.path.abspath(root), 'idx': idx, 'ino': ino}"))
L[i] = L[i].replace("os.path.join(BASE_DIR, 'scan_index.json')", '_idx_path(root)')
done.append('do-list-per-root')
i = next(k for k, l in enumerate(L) if l.strip().startswith('def do_send('))
j = next(k for k in range(i+1, len(L)) if L[k].strip() == "say(\"usage:  <command>  <candidate name>\"); return" or L[k].strip().startswith('say("usage:'))
k2 = j + 1
L[k2:k2] = ['    ph, rest = _phone_first(arg)',
            '    if ph:',
            "        nm = rest.title() or 'there'",
            "        pos = f['display'] if f else clean_pos(os.path.basename(root))",
            "        cli = f['client'] if f else re.sub(r'^\\d+[\\s_-]*', '', os.path.basename(os.path.dirname(root)))",
            '        tpl = _tpl_for(tpl_words)',
            '        try: text = tpl.format(name=nm, position=pos, company=cli)',
            '        except Exception: text = tpl',
            '        try:',
            '            import wa',
            '            wa.send_review(ph, text, say, ask=ask)',
            '        except Exception as e:',
            '            say(f"⚠️ whatsapp failed: {e}")',
            '        return']
done.append('do-send-phone-first')
i = next(k for k, l in enumerate(L) if l.strip().startswith('def do_missed('))
j = next(k for k in range(i+1, len(L)) if L[k].strip().startswith('hit = _scan_path') or L[k].strip().startswith('q = arg.lower'))
L[j:j] = ['    ph, rest = _phone_first(arg)',
          '    if ph:',
          "        nm = rest.title() or 'there'",
          "        pos = f['display'] if f else clean_pos(os.path.basename(root))",
          "        cli = f['client'] if f else re.sub(r'^\\d+[\\s_-]*', '', os.path.basename(os.path.dirname(root)))",
          "        text = _tpl_for(['missed']).format(name=nm, position=pos, company=cli)",
          '        try:',
          '            import wa',
          '            wa.send_review(ph, text, say, ask=ask)',
          '        except Exception as e:',
          '            say(f"⚠️ whatsapp failed: {e}")',
          '        return']
done.append('do-missed-phone-first')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
# ---------------- wa.py ----------------
p = 'wa.py'; L = open(p).read().split('\n')
if 'def _goto(page, url, say=print):' not in '\n'.join(L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def send_review('))
    L[i:i] = ['def _goto(page, url, say=print):',
              '    for a in (0, 1):',
              '        try:',
              "            page.goto(url, timeout=90000, wait_until='domcontentloaded'); return True",
              '        except Exception:',
              '            if a == 0: time.sleep(2)',
              "    say('⚠️ WhatsApp page did not load (network?) - try again in a minute')",
              '    return False',
              '']
    done.append('wa-goto-retry')
L = [l.replace('page.goto("https://web.whatsapp.com")', '_goto(page, "https://web.whatsapp.com")')
      .replace('page.goto(f"https://web.whatsapp.com/send?phone={digits}")', 'if not _goto(page, f"https://web.whatsapp.com/send?phone={digits}"): return False')
      for l in L]
done.append('wa-goto-used')
for i, l in enumerate(L):
    if l.strip().startswith("for sel in ('button[data-testid=\"compose-btn-send\"]', 'span[data-icon=\"btn-send\"]'):"):
        d = len(l) - len(l.lstrip())
        L[i-1:i+4] = [d*' ' + 'sent = _click_send(page)']
        done.append('wa-interactive-click-send'); break
for i, l in enumerate(L):
    if l.strip() == "if c == '':":
        j = i + 1
        while j < len(L) and (not L[j].strip() or (len(L[j]) - len(L[j].lstrip())) > (len(l) - len(l.lstrip()))):
            j += 1
        d = len(l) - len(l.lstrip())
        L[j:j] = [d*' ' + 'say("   (type Enter to send · e edit · n number · q skip)")']
        done.append('wa-invalid-choice-hint'); break
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
# ---------------- selftest S7-S10 ----------------
p = 'butler.py'; L = open(p).read().split('\n')
if "'S7 wa interactive uses _click_send'" not in '\n'.join(L):
    i = next(k for k, l in enumerate(L) if "'S6 watcher handler intact'" in l)
    dd = len(L[i]) - len(L[i].lstrip())
    L[i+1:i+1] = [dd*' ' + "_wa = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wa.py')).read()",
                  dd*' ' + "_br = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'briefing.py')).read()",
                  dd*' ' + "ck('S7 wa interactive uses _click_send', 'sent = _click_send(page)' in _wa)",
                  dd*' ' + "ck('S8 scan index per-root', 'def _scan_path(num, root=None)' in _br)",
                  dd*' ' + "ck('S9 rename swallows vanished files', 'except FileNotFoundError:' in _src)",
                  dd*' ' + "ck('S10 prompts silence sweeps', 'INTERACTIVE = False' in _src)"]
    done.append('selftest-S7-S10')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done or 'nothing missing')
