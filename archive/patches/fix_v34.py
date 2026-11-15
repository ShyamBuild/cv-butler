import ast
p = 'briefing.py'; L = open(p).read().split('\n'); done = []
def ind(l): return len(l) - len(l.lstrip())
if not any(l.strip() == 'import sys' or l.strip().startswith('import sys') for l in L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('import '))
    L.insert(i, 'import sys'); done.append('sys-import')
if 'def _cli(argv):' not in '\n'.join(L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith("if __name__ == '__main__':"))
    CLI = ['def _cli_root():',
           '    f = _read_focus()',
           "    if f: return f['path']",
           '    try:',
           "        r = open(os.path.expanduser('~/.cvtool_last_butler_root')).read().strip()",
           '        if r and os.path.isdir(r): return r',
           '    except Exception:',
           '        pass',
           "    raise SystemExit('no focus and no last butler root - set one: cv_env/bin/python3 briefing.py chat  then: focus <position>')",
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
    done.append('cli-functions')
    i = next(k for k, l in enumerate(L) if l.strip().startswith("if __name__ == '__main__':"))
    j = i + 1
    while j < len(L) and (not L[j].strip() or ind(L[j]) >= 1):
        j += 1
    if j < len(L) and L[j].strip() == 'main()':
        j += 1
    L[i:j] = ["if __name__ == '__main__':",
              '    if len(sys.argv) > 1:',
              '        _cli(sys.argv[1:])',
              '    else:',
              '        main()']
    done.append('cli-main')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
p = 'butler.py'; L = open(p).read().split('\n')
if "'S12 briefing CLI one-shot'" not in '\n'.join(L):
    i = next(k for k, l in enumerate(L) if "'S11 missed works without focus" in l)
    d = ind(L[i])
    L.insert(i+1, d*' ' + "ck('S12 briefing CLI one-shot', 'def _cli(argv):' in _br)")
    done.append('S12-guard')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done or 'nothing missing')
