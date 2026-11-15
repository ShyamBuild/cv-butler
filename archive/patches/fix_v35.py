import ast
rep = {f: open(f).read().split('\n') for f in ('butler.py', 'briefing.py')}
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
def fndef(L, name):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def ' + name + '('))
    d = ind(L[i]); j = i + 1
    while j < len(L) and (not L[j].strip() or ind(L[j]) > d): j += 1
    return i, j
def phone_block(tpl):
    return ['    ph0, rest0 = _phone_first(arg)',
            '    if ph0:',
            "        nm = rest0.title() or 'there'",
            "        pos = f['display'] if f else clean_pos(os.path.basename(root))",
            "        cli = f['client'] if f else re.sub(r'^\\d+[\\s_-]*', '', os.path.basename(os.path.dirname(root)))",
            '        text = ' + tpl + '.format(name=nm, position=pos, company=cli)',
            '        try:',
            '            import wa',
            '            wa.send_review(ph0, text, say, ask=ask)',
            '        except Exception as e:',
            '            say(f"⚠️ whatsapp failed: {e}")',
            '        return']
def mk_strip(fn):
    def f(L):
        i, j = fndef(L, fn)
        if any("arg = (arg or '').strip()" in l for l in L[i:j]): return L
        L.insert(i+1, '    arg = (arg or \'\').strip()')
        return L
    return f
def mk_phone(fn, tpl):
    def f(L):
        i, j = fndef(L, fn)
        if any('_phone_first(arg)' in l for l in L[i:j]): return L
        k = next((x for x in range(i+1, j) if L[x].strip().startswith('hit = _scan_path') or L[x].strip().startswith('q = arg.lower')), None)
        if k is None: return L
        L[k:k] = phone_block(tpl)
        return L
    return f
for fn in ('do_missed', 'do_send', 'do_wa'):
    edit('briefing.py', fn + '-strip', mk_strip(fn))
edit('briefing.py', 'do_missed-phone', mk_phone('do_missed', "_tpl_for(['missed'])"))
edit('briefing.py', 'do_send-phone', mk_phone('do_send', "_tpl_for(tpl_words)"))
def cli(L):
    if 'def _cli(argv):' in L: return L
    i = next(k for k, l in enumerate(L) if l.strip().startswith('if __name__'))
    CLI = ['def _cli_root():',
           '    f = _read_focus()',
           "    if f: return f['path']",
           '    try:',
           "        r = open(os.path.expanduser('~/.cvtool_last_butler_root')).read().strip()",
           '        if r and os.path.isdir(r): return r',
           '    except Exception:',
           '        pass',
           "    raise SystemExit('no focus and no last butler root - open chat and: focus <position>')",
           'def _cli(argv):',
           '    cmd = argv[0].lower(); arg = " ".join(argv[1:])',
           '    root = _cli_root()',
           "    if cmd == 'missed': do_missed(arg, root, print)",
           "    elif cmd == 'wa': do_wa(arg, root, print)",
           "    elif cmd == 'jd': do_send(arg, root, ['jd shared'], print)",
           "    elif cmd == 'nudge': do_send(arg, root, ['nudge'], print)",
           "    elif cmd == 'touch': do_send(arg, root, ['touch'], print)",
           "    elif cmd in ('brief', 'board'): print_briefing(root)",
           "    else: print('cli: missed | wa | jd | nudge | touch | brief  <args>')",
           '']
    L[i:i] = CLI
    j = next(k for k, l in enumerate(L) if l.strip().startswith('if __name__'))
    L.insert(j+1, "    if len(sys.argv) > 1 and sys.argv[1].lower() in ('missed','wa','jd','nudge','touch','brief','board'):")
    L.insert(j+2, '        _cli(sys.argv[1:]); raise SystemExit(0)')
    return L
edit('briefing.py', 'cli-one-shot', cli)
edit('butler.py', 'console-missed-slice', lambda L: [l.replace('do_missed(raw[6:]', 'do_missed(raw[7:]') for l in L])
def s13(L):
    if "'S13 missed phone-first" in '\n'.join(L): return L
    i = next(k for k, l in enumerate(L) if "'S12 briefing CLI one-shot'" in l or "'S11 missed works without focus" in l)
    d = ind(L[i])
    L.insert(i+1, d*' ' + "ck('S13 missed phone-first + strip', '_phone_first(arg)' in _br and \"arg = (arg or '').strip()\" in _br)")
    return L
edit('butler.py', 'S13-guard', s13)
for f in rep:
    open(f, 'w').write('\n'.join(rep[f]))
print('✅ applied:', done)
print('⏭ skipped:', skipped or 'none')
