import ast, json, os
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
LOG = ["class StageLog:",
       "    def __init__(self, root):",
       "        self.path = os.path.join(root, 'stage_log.json')",
       "        self.data = {}",
       "        try:",
       "            if os.path.exists(self.path):",
       "                self.data = json.load(open(self.path))",
       "        except Exception:",
       "            self.data = {}",
       "    def _save(self):",
       "        try:",
       "            tmp = self.path + '.tmp'",
       "            json.dump(self.data, open(tmp, 'w'), indent=2)",
       "            os.replace(tmp, self.path)",
       "        except Exception:",
       "            pass",
       "    def _n(self, s): return (s or '').strip().lower()",
       "    def observe(self, name, stage, position):",
       "        k = self._n(name)",
       "        if not k or not stage: return",
       "        cur = self.data.get(k, [])",
       "        if cur and cur[-1].get('stage') == stage and cur[-1].get('position') == position: return",
       "        cur.append({'stage': stage, 'position': position, 'ts': int(time.time())})",
       "        self.data[k] = cur[-50:]",
       "        self._save()",
       "    def latest(self, name):",
       "        cur = self.data.get(self._n(name), [])",
       "        return cur[-1] if cur else None",
       "    def all_for(self, name):",
       "        return list(reversed(self.data.get(self._n(name), [])))",
       ""]
def e1(L):
    if 'class StageLog:' in '\n'.join(L): return L
    i = next(k for k, l in enumerate(L) if l.strip().startswith('class Butler:'))
    L[i:i] = LOG
    return L
edit('butler.py', 'stagelog-class', e1)
def e2(L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def __init__(self, root)'))
    if 'self.slog = StageLog(root)' in '\n'.join(L[i:i+15]): return L
    d = ind(L[i])
    L.insert(i+1, d*' ' + '    self.slog = StageLog(root)')
    return L
edit('butler.py', 'butler-init-slog', e2)
def e3(L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def _reconcile_tags(self'))
    if 'self.slog.observe' in '\n'.join(L[i:i+60]): return L
    mv = next(k for k in range(i+1, min(i+60, len(L))) if 'shutil.move(src, dst)' in L[k])
    d = ind(L[mv])
    L.insert(mv+1, d*' ' + '        try:',
    )
    # insert a multi-line block after the move
    L[mv+1:mv+1] = [
        d*' ' + '            try:',
        d*' ' + '                _nm = os.path.splitext(os.path.basename(src))[0]',
        d*' ' + "                _st = os.path.basename(os.path.dirname(dst))",
        d*' ' + '                _ps = self.position_folder_for(src)',
        d*' ' + '                _pn = os.path.relpath(_ps, self.root) if _ps.startswith(self.root) else os.path.basename(_ps or "")',
        d*' ' + '                self.slog.observe(_nm, _st, _pn)',
        d*' ' + '            except Exception:',
        d*' ' + '                pass',
    ]
    return L
edit('butler.py', 'reconcile-observe', e3)
def e4(L):
    if 'def do_history(' in '\n'.join(L): return L
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def do_missed('))
    d = ind(L[i])
    H = [d*' ' + 'def do_history(arg, root, say=print):',
         d*' ' + '    from butler import StageLog',
         d*' ' + "    if not arg: say('usage: history <name>'); return",
         d*' ' + '    slog = StageLog(root)',
         d*' ' + '    rows = slog.all_for(arg)',
         d*' ' + "    if not rows: say(f'no history for {arg!r}'); return",
         d*' ' + '    say(f"{arg}:")',
         d*' ' + '    import datetime as _dt',
         d*' ' + '    for r in rows:',
         d*' ' + "        d = _dt.datetime.fromtimestamp(r['ts']).strftime('%Y-%m-%d')",
         d*' ' + "        say(f\"  {d} · {r['stage']} · {r.get('position','')}\")",
         d*' ' + 'def do_stale(arg, root, say=print):',
         d*' ' + '    from butler import StageLog',
         d*' ' + "    days = int(arg) if (arg or '').strip().isdigit() else 7",
         d*' ' + '    slog = StageLog(root)',
         d*' ' + '    now = int(time.time())',
         d*' ' + '    out = []',
         d*' ' + '    for k, entries in slog.data.items():',
         d*' ' + '        if not entries: continue',
         d*' ' + '        last = entries[-1]',
         d*' ' + "        age = (now - last['ts']) // 86400",
         d*' ' + '        if age >= days:',
         d*' ' + "            out.append((age, k.title(), last['stage'], last.get('position','')))",
         d*' ' + "    if not out: say(f'nothing older than {days}d'); return",
         d*' ' + "    say(f'🕑 stale (>{days}d):')",
         d*' ' + "    for age, nm, st, ps in sorted(out, reverse=True):",
         d*' ' + "        say(f'  {age:3d}d · {nm:<24s} · {st} · {ps}')",
         '']
    L[i:i] = H
    return L
edit('briefing.py', 'history-and-stale', e4)
def e5(L):
    for k, l in enumerate(L):
        if l.strip().startswith("elif cmd == 'nudge'") or l.strip().startswith("elif cmd == 'missed'"):
            if any("cmd == 'history'" in x for x in L[k:k+15]): return L
            L.insert(k+1, ind(l)*' ' + "    elif cmd == 'history': do_history(arg, root, print)",
            )
            L.insert(k+2, ind(l)*' ' + "    elif cmd == 'stale': do_stale(arg, root, print)")
            return L
    return L
edit('briefing.py', 'cli-routes', e5)
def e6(L):
    if 'history <name>' in '\n'.join(L): return L
    for k, l in enumerate(L):
        if 'missed  <number> <Name>' in l:
            L.insert(k+1, ind(l)*' ' + 'history <name>       .. stage transitions for one candidate')
            L.insert(k+2, ind(l)*' ' + 'stale [days]         .. candidates in current stage longer than N days (default 7)')
            return L
    return L
edit('briefing.py', 'help-card-history-stale', e6)
def e7(L):
    if "'S21 stage ageing" in '\n'.join(L): return L
    i = next(k for k, l in enumerate(L) if "'S20 sweep scoping" in l)
    d = ind(L[i])
    L.insert(i+1, d*' ' + "ck('S21 stage ageing + history + stale', 'class StageLog:' in _src and 'def do_history(' in _br and 'def do_stale(' in _br)")
    return L
edit('butler.py', 'S21-guard', e7)
for f in rep:
    open(f, 'w').write('\n'.join(rep[f]))
print('✅ applied:', done)
print('⏭ skipped:', skipped or 'none')
