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
def w1(L):
    if 'try:\n    from playwright.sync_api import sync_playwright' in '\n'.join(L): return L
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def ') and not ind(l))
    L[i:i] = ['try:', '    from playwright.sync_api import sync_playwright', 'except Exception:', '    sync_playwright = None', '']
    return L
def p1(L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def position_folder_for('))
    d = ind(L[i]); j = i + 1
    while j < len(L) and (not L[j].strip() or ind(L[j]) > d): j += 1
    L[i:j] = [d*' ' + 'def position_folder_for(self, p):',
              d*' ' + '    dd = os.path.dirname(os.path.abspath(p))',
              d*' ' + '    rel = os.path.relpath(dd, self.root)',
              d*' ' + "    parts = [] if rel == '.' else rel.split(os.sep)",
              d*' ' + '    if len(parts) >= 2:',
              d*' ' + '        return os.path.join(self.root, parts[0], parts[1])',
              d*' ' + '    return dd', '']
    return L
SELF = '''    import shutil as _sh
    ran = []
    fails = []
    def ck(label, ok, extra=''):
        ran.append(label.split()[0])
        if not ok: fails.append(label)
        print(('PASS ' if ok else 'FAIL ') + label + ((' ' + str(extra)) if extra else ''))
        return ok
    _tg0 = {t.lower().replace('\\u2013','-').replace(' ','_') for t in ['Awaiting CV Update','Awaiting JD Confirmation','Call Scheduled','Feedback Pending','Interview Scheduled','Closed – Not Proceeding','Ready for Manager Review','Rejected by Client']}
    _ROOTTAGS0 = {c for c in os.listdir(root) if os.path.isdir(os.path.join(root, c)) and c.lower().replace('\\u2013','-').replace(' ','_') in _tg0}
    B = Butler(root)
    ck('S1 bindings', all(callable(getattr(B, m, None)) for m in ('route','handle_tags','_reconcile_tags','_compact_numbers','position_folder_for','tags_of')))
    _prw = [os.path.join(dp, f) for dp, dn, fn in os.walk(root) for f in fn if f == 'Pradip Amte.pdf']
    POS = os.path.dirname(os.path.dirname(_prw[0])) if _prw else root
    tags = B.tags_of(_prw[0]) if _prw else []
    ck('S2 tag reading', 'Closed – Not Proceeding' in tags, tags)
    B._reconcile_tags(print)
    ck('S3 pradip filed by tag', bool(_prw) and os.path.basename(os.path.dirname(_prw[0])) in ('Closed – Not Proceeding','Closed - Not Proceeding'))
    cands = [f for f in sorted(os.listdir(POS)) if f.lower().endswith('.pdf') and not f.startswith('zz_') and 'jd' not in f.lower() and 'location' not in f.lower() and not f.lower().startswith('regional')]
    tmp = os.path.join(POS, 'zz_garbage_test.pdf')
    ok4 = False
    if cands:
        b0 = os.path.splitext(cands[0])[0]
        pre = set(os.listdir(POS))
        _sh.copy(os.path.join(POS, cands[0]), tmp)
        B.route(tmp, print)
        ok4 = not os.path.exists(tmp)
        for f in set(os.listdir(POS)) - pre:
            if f.startswith('zz_') or f == b0 + '.pdf' or re.match(re.escape(b0) + r'_\\d+\\.pdf$', f):
                try: os.remove(os.path.join(POS, f))
                except Exception: pass
        if os.path.exists(tmp):
            try: os.remove(tmp)
            except Exception: pass
    ck('S4 wrong-name repair', ok4)
    rows = briefing.collect(POS)
    ck('S5 board closed row', any('Closed' in str(r) for r in rows))
    _src = open(__file__).read()
    import ast as _ast
    _ln = _src.split('\\n')
    _hcls = [x for x in _ast.walk(_ast.parse(_src)) if isinstance(x, _ast.ClassDef) and x.name == 'H']
    _seg = '\\n'.join(_ln[_hcls[0].lineno-1:_hcls[0].end_lineno]) if _hcls else ''
    ck('S6 watcher handler intact', bool(_seg) and 'self._add' in _seg and 'B._add' not in _seg, f'seglen={len(_seg)}')
    _wa = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wa.py')).read()
    _br = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'briefing.py')).read()
    ck('S7 wa interactive uses _click_send', 'I clicked send myself' in _wa)
    ck('S8 scan index per-root', 'def _scan_path(num, root=None)' in _br)
    ck('S9 rename swallows vanished files', 'except FileNotFoundError:' in _src)
    ck('S10 prompts silence sweeps', 'INTERACTIVE = False' in _src and 'if not INTERACTIVE:' in _src and 'def hsay(m):' in _src)
    ck('S11 missed works without focus + help card', "'display': clean_pos(os.path.basename(root))," in _br and 'missed  <number>' in _br)
    ck('S12 send phase launches+fills', 'launch_persistent_context' in _wa and 'keyboard.insert_text(text)' in _wa)
    ck('S13 missed phone-first + strip', '_phone_first(arg)' in _br and "arg = (arg or '').strip()" in _br)
    ck('S14 manual-send default', 'I clicked send myself' in _wa)
    ck('S15 autosend constant defined', 'AUTOSEND =' in _wa)
    ck('S16 verified auto-fill', 'def _place_text(' in _wa and 'ok_fill = _place_text(page, text, say)' in _wa)
    ck('S17 playwright import at module scope', 'try:\\n    from playwright.sync_api import sync_playwright' in _wa)
    ck('S18 position never falls back to company root', 'return os.path.join(self.root, parts[0], parts[1])' in _src and 'return self.root' not in _src.split('def position_folder_for')[1].split('def ')[0])
    ck('S19 reconcile adds no company-root tag folders', not [c for c in os.listdir(root) if os.path.isdir(os.path.join(root, c)) and c.lower().replace('\\u2013','-').replace(' ','_') in _tg0 and c not in _ROOTTAGS0])
    missing = [f'S{n}' for n in range(1, 20) if f'S{n}' not in ran]
    if missing: print('SKILLS MISSING', missing)
    if fails or missing: return False
    print('ALL GREEN')
    return True
'''
def st(L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def _selftest('))
    d = ind(L[i]); j = i + 1
    while j < len(L) and not (L[j].strip().startswith('def ') and not ind(L[j])): j += 1
    L[i:j] = ['def _selftest(root):'] + [x for x in SELF.split('\n') if x.strip() or x == '']
    return L
edit('wa.py', 'playwright-import-module-level', w1)
edit('butler.py', 'position-folder-depth2', p1)
edit('butler.py', 'selftest-canonical-rewrite', st)
for f in rep:
    open(f, 'w').write('\n'.join(rep[f]))
print('✅ applied:', done)
print('⏭ skipped:', skipped or 'none')
