import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def _pl_root(' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def _jd_like_name('))
    B[i:i] = ["def _pl_root():  # PIPELINE v83.0: the world is the workspace the lock names",
              "    try:",
              "        for f in os.listdir(BASE_DIR):",
              "            if f.startswith('butler_') and f.endswith('.lock'):",
              "                return open(os.path.join(BASE_DIR, f)).read().split('|', 1)[1].strip()",
              "    except Exception:",
              "        pass",
              "    return os.path.join(os.path.expanduser('~'), 'Downloads', 'Sunsoft Technology')",
              "def _tags_of(p):  # PIPELINE v83.0: the tag is the ledger's only input",
              "    try:",
              "        arr = plistlib.loads(_xattr_raw(p, 'com.apple.metadata:_kMDItemUserTags')) or []",
              "        out = []",
              "        for t in arr:",
              "            if isinstance(t, bytes): t = t.decode('utf-8', 'ignore')",
              "            t = str(t).strip()",
              "            if t: out.append(t)",
              "        return out",
              "    except Exception:",
              "        return []",
              "PIPELINE_CLOCKED = {'Ready for Manager Review': 'eod', 'Feedback Pending': 86400, 'Shortlisted for Interview': 172800, 'Interview Cleared': 172800, 'Expected to Join': 259200, 'Joined - Payment Pending': 259200}  # PIPELINE-CLOCKS v83.0",
              "PIPELINE_MOMENT = ('Call Scheduled', 'Interview Scheduled', 'Interview Today', 'Interview Tomorrow')",
              "PIPELINE_TERMINAL = ('Rejected by Client', 'Closed \\u2013 Not Proceeding', 'Payment Received')",
              "PIPELINE_PRE = ('Awaiting JD Confirmation', 'Awaiting CV Update')",
              "def _pl_eod_ts(ts):",
              "    st = time.localtime(ts)",
              "    return int(time.mktime((st.tm_year, st.tm_mon, st.tm_mday, 16, 30, 0, 0, 0, -1)))",
              "def _pl_due(entry):",
              "    sla = PIPELINE_CLOCKED.get(entry.get('tag'), 0)",
              "    return _pl_eod_ts(entry['since']) if sla == 'eod' else entry['since'] + sla",
              "def _pl_age(now, since):",
              "    d = (now - since) // 86400",
              "    return f'{d}d' if d else f'{max(1, (now - since) // 3600)}h'",
              "def _pl_load():",
              "    lp = os.path.join(BASE_DIR, 'pipeline.json')",
              "    return (json.load(open(lp)) if os.path.exists(lp) else {}), lp",
              "def _pl_clientpos(path, root):",
              "    parts = os.path.relpath(path, root).split(os.sep)",
              "    return (parts[0] if len(parts) > 2 else ''), (parts[1] if len(parts) > 2 else (parts[0] if len(parts) > 1 else ''))",
              "def pipeline_pending(filt=None, say=print):",
              "    led, _ = _pl_load(); now = int(time.time()); root = _pl_root(); shown = 0",
              "    groups = {}",
              "    for p, e in led.items():",
              "        if e.get('closed'): continue",
              "        blob = ' '.join([e.get('tag', ''), e.get('client', ''), e.get('position', '')]).lower()",
              "        if filt and filt.lower() not in blob: continue",
              "        groups.setdefault((e.get('client', ''), e.get('position', '')), []).append((p, e))",
              "    for (cl, po), rows in sorted(groups.items()):",
              "        say(f\"\\U0001f3e2 {cl or '?'} · {po or '?'}\")",
              "        for p, e in sorted(rows, key=lambda x: x[1]['since']):",
              "            od = ' ⚠️ overdue' if e.get('tag') in PIPELINE_CLOCKED and now >= _pl_due(e) else ''",
              "            mk = '🕐' if e.get('tag') in PIPELINE_MOMENT else '⏳'",
              "            say(f\"   {mk} {os.path.basename(p)} · {e.get('tag')} · {_pl_age(now, e['since'])}{od}\"); shown += 1",
              "    if filt and filt.lower() == 'pre':",
              "        for dp, dn, fn in os.walk(root):",
              "            for x in fn:",
              "                if x.lower().endswith(('.pdf', '.docx')):",
              "                    tg = [t for t in _tags_of(os.path.join(dp, x)) if t in PIPELINE_PRE]",
              "                    if tg: say(f\"   🧰 {x} · {tg[0]} (your prep, not your debt)\"); shown += 1",
              "    if not shown: say('📭 nothing pending - the pipeline is empty right now')",
              "def pipeline_status(name, say=print):",
              "    led, _ = _pl_load(); now = int(time.time()); toks = (name or '').lower().split(); found = 0",
              "    for p, e in led.items():",
              "        st = os.path.splitext(os.path.basename(p))[0].lower()",
              "        if toks and all(t in st.split() or t in st for t in toks):",
              "            found += 1",
              "            say(f\"\\U0001faaa {os.path.basename(p)} · {e.get('client')} · {e.get('position')}\")",
              "            for h in e.get('history', []): say(f\"   · {h[0]} · {_pl_age(h[2], h[1])} then\")",
              "            if e.get('closed'): say(f\"   · closed: {e.get('closed_tag') or e.get('tag')} · {_pl_age(now, e['closed'])} ago\")",
              "            else:",
              "                od = ' ⚠️ overdue' if e.get('tag') in PIPELINE_CLOCKED and now >= _pl_due(e) else ''",
              "                say(f\"   · now: {e.get('tag')} · {_pl_age(now, e['since'])}{od}\")",
              "            for n in e.get('notes', [])[-3:]: say(f\"   💬 {n['text']} ({_pl_age(now, n['ts'])} ago)\")",
              "    if not found: say(f'🤷 no pipeline row for {name or \"?\"}')",
              "def pipeline_note(name, text, say=print):",
              "    led, lp = _pl_load(); now = int(time.time()); toks = (name or '').lower().split(); found = 0",
              "    for p, e in led.items():",
              "        st = os.path.splitext(os.path.basename(p))[0].lower()",
              "        if toks and all(t in st.split() or t in st for t in toks):",
              "            found += 1",
              "            notes = e.setdefault('notes', [])",
              "            notes.append({'text': text, 'ts': now})",
              "            json.dump(led, open(lp, 'w'), indent=1)",
              "            say(f'\\U0001f4dd noted for {os.path.basename(p)}: {text}')",
              "    if not found: say(f'\\U0001f937 no pipeline row for {name or \"?\"}')",
              ""]
    done.append('pipeline-helpers')
    src = '\n'.join(B)
if 'def _pipeline_reconcile(' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def _autodraft_tick('))
    B[i:i] = ["    def _pipeline_reconcile(self, say=print):  # PIPELINE-RECONCILE v83.0",
              "        try:",
              "            led, lp = _pl_load(); now = int(time.time()); root = _pl_root(); changed = False",
              "            if not getattr(self, '_pl_boot', False):",
              "                self._pl_boot = True; seeded = 0",
              "                for dp, dn, fn in os.walk(root):",
              "                    for x in fn:",
              "                        if x.lower().endswith(('.pdf', '.docx')):",
              "                            pp = os.path.join(dp, x)",
              "                            tg = next((t for t in _tags_of(pp) if t in PIPELINE_CLOCKED or t in PIPELINE_MOMENT), None)",
              "                            if tg and pp not in led:",
              "                                cl, po = _pl_clientpos(pp, root)",
              "                                led[pp] = {'tag': tg, 'since': now, 'history': [], 'client': cl, 'position': po, 'closed': None}; seeded += 1; changed = True",
              "                if seeded: say(f'📒 pipeline ledger seeded with {seeded} already-tagged candidate(s) - clocks start now')",
              "            for fp, adds in list(getattr(self, '_added_tags', {}).items()):",
              "                tg = next((t for t in adds if t in PIPELINE_CLOCKED or t in PIPELINE_MOMENT), None)",
              "                if tg and (fp not in led or led[fp].get('closed')):",
              "                    cl, po = _pl_clientpos(fp, root)",
              "                    led[fp] = {'tag': tg, 'since': now, 'history': [], 'client': cl, 'position': po, 'closed': None}; changed = True",
              "            for p in list(led):",
              "                e = led[p]",
              "                if e.get('closed'): continue",
              "                tgs = _tags_of(p) if os.path.exists(p) else []",
              "                cur = next((t for t in tgs if t in PIPELINE_CLOCKED or t in PIPELINE_MOMENT), None)",
              "                term = next((t for t in tgs if t in PIPELINE_TERMINAL), None)",
              "                if term:",
              "                    e['history'].append([e['tag'], e['since'], now]); e['closed'] = now; e['closed_tag'] = term; changed = True",
              "                    say(f\"✅ {os.path.basename(p)} closed ({term}) - ledger row archived\"); continue",
              "                if cur is None:",
              "                    e['history'].append([e['tag'], e['since'], now]); e['closed'] = now; e['closed_tag'] = 'tag removed'; changed = True",
              "                    say(f\"📔 {os.path.basename(p)} left the pipeline (tag removed)\"); continue",
              "                if cur != e['tag']:",
              "                    e['history'].append([e['tag'], e['since'], now]); e['tag'] = cur; e['since'] = now; e.pop('chased', None); changed = True",
              "            od = [ (p, e) for p, e in led.items() if not e.get('closed') and e.get('tag') in PIPELINE_CLOCKED and now >= _pl_due(e) ]",
              "            if od:  # PIPELINE-NUDGE-REST v83.0",
              "                key = f\"{len(od)}:{min(e['since'] for _, e in od)}\"",
              "                nst = led.setdefault('_nudge', {})",
              "                if nst.get('key') != key or now - nst.get('ts', 0) >= 4 * 3600:",
              "                    say('⏰ ' + '; '.join(f\"{os.path.basename(p)} ({e.get('client')}·{e.get('position')}, {_pl_age(now, e['since'])} in {e['tag']})\" for p, e in od[:6]) + (' …' if len(od) > 6 else ''))",
              "                    nst['key'] = key; nst['ts'] = now; changed = True",
              "                for p, e in od:",
              "                    if not e.get('chased'):",
              "                        try: cadence.queue(os.path.splitext(os.path.basename(p))[0], 'feedback_chase', note=f\"{e['tag']} {_pl_age(now, e['since'])}\", due=now)",
              "                        except Exception: pass",
              "                        e['chased'] = now; changed = True",
              "            if changed: json.dump(led, open(lp, 'w'), indent=1)",
              "        except Exception as _ple:",
              "            say(f'⚠️ pipeline reconcile skipped: {_ple}')",
              ""]
    done.append('pipeline-method')
    src = '\n'.join(B)
if 'self._pipeline_reconcile(' not in src:
    for k, l in enumerate(B):
        if l.strip().startswith('def _autodraft_tick(self, say=print):'):
            B.insert(k+1, '        self._pipeline_reconcile(say)  # PIPELINE-RECONCILE v83.0: the first breath of the tick reconciles the pipeline before any flag is read')
            done.append('pipeline-hook'); break
    src = '\n'.join(B)
if "sys.argv[1] == 'pending'" not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'sys.exit(0 if _selftest(sys.argv[2]) else 1)')
    B[i:i] = ["if len(sys.argv) > 1 and sys.argv[1] == 'pending':",
              "    pipeline_pending(sys.argv[2] if len(sys.argv) > 2 else None, print); sys.exit(0)",
              "if len(sys.argv) > 1 and sys.argv[1] == 'status':",
              "    pipeline_status(' '.join(sys.argv[2:]), print); sys.exit(0)",
              "if len(sys.argv) > 1 and sys.argv[1] == 'note':",
              "    pipeline_note(sys.argv[2], ' '.join(sys.argv[3:]), print); sys.exit(0)"]
    done.append('pipeline-cli')
    src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
srcg = '\n'.join(g)
if 'def do_pending(' not in srcg:
    i = next(k for k, l in enumerate(g) if l.startswith('def do_missed('))
    g[i:i] = ["def do_pending(arg, root, say=print):",
              "    butler.pipeline_pending(arg or None, say)",
              "def do_status(arg, root, say=print):",
              "    butler.pipeline_status(arg, say)",
              "def do_note(arg, root, say=print):",
              "    parts = arg.split(' ', 1)",
              "    if len(parts) < 2: say('usage: note <name> <text>'); return",
              "    butler.pipeline_note(parts[0], parts[1], say)",
              ""]
    done.append('pipeline-chat-fns')
    srcg = '\n'.join(g)
if not any(l.strip().startswith('do_pending(') for l in g):
    for k, l in enumerate(g):
        if l.strip() == 'do_missed(q[6:], root); continue':
            d = ind(l)
            g[k:k] = [d*' ' + "do_pending(q[len('pending'):].strip(), root); continue",
                      d*' ' + "do_status(q[len('status'):].strip(), root); continue",
                      d*' ' + "do_note(q[len('note'):].strip(), root); continue"]
            done.append('pipeline-chat-dispatch'); break
    srcg = '\n'.join(g)
if srcg != open(G).read():
    ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S210 the pipeline reconcile runs whether or not the bell is muted", "'S209 the machine's own voice rests, the master's never", "ck('S210 the pipeline reconcile runs whether or not the bell is muted', (chr(35)+' PIPELINE-RECONCILE v83.0') in _src and ('self._pipeline_reconcile(' in _src))"),
      ("'S211 one ledger, two doors - chat and terminal ask the same clerk", "'S210 the pipeline reconcile runs whether or not the bell is muted", "ck('S211 one ledger, two doors - chat and terminal ask the same clerk', ('def pipeline_pending(' in _src) and ('def do_pending(' in open(os.path.join(BASE_DIR, 'briefing.py')).read()) and (\"sys.argv[1] == 'pend\"+'ing') in _src)"),
      ("'S212 the overdue nudge rests like every machine-born voice", "'S211 one ledger, two doors - chat and terminal ask the same clerk", "ck('S212 the overdue nudge rests like every machine-born voice', (chr(35)+' PIPELINE-NUDGE-REST v83.0') in _src)"),
      ("'S213 terminal tags never clock", "'S212 the overdue nudge rests like every machine-born voice", "ck('S213 terminal tags never clock', ('PIPELINE_TERMINAL' in _src) and ('Rejected by Client' not in _src[_src.find('PIPELINE_CLOCKED'):_src.find('PIPELINE_MOMENT')]))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S208 the class keeps its methods")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
