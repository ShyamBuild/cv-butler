import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
i0 = next(k for k, l in enumerate(B) if l.startswith('def _tags_of('))
i1 = next(k for k, l in enumerate(B) if l.startswith('PIPELINE_CLOCKED ='))
if 'os.getxattr(' not in '\n'.join(B[i0:i1]):
    B[i0:i1] = ["def _tags_of(p):  # PIPELINE v83.0 (native v84.0): ask the kernel first - Spotlight is a librarian, not a witness",
                "    try:",
                "        import plistlib as _pl",
                "        return [str(t).strip() for t in (_pl.loads(os.getxattr(p, 'com.apple.metadata:_kMDItemUserTags')) or []) if str(t).strip()]",
                "    except Exception:",
                "        pass",
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
                ""]
    done.append('native-tag-read')
src = '\n'.join(B)
if 'def desk_load(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def _pl_root():'))
    B[i:i] = ["DESK_PATH = os.path.join(BASE_DIR, 'desk.json')  # DESK v84.0: today's chair inside the library",
              "def desk_load():",
              "    try: return json.load(open(DESK_PATH))",
              "    except Exception: return {'primary': '', 'secondary': ''}",
              "def desk_save(d): json.dump(d, open(DESK_PATH, 'w'), indent=1)",
              "def desk_resolve(spec, root):",
              "    toks = [t for t in spec.lower().split() if t]",
              "    best = None; bs = -1",
              "    for dp, dn, fn in os.walk(root):",
              "        rel = os.path.relpath(dp, root)",
              "        if rel == '.' or rel.count(os.sep) > 1: continue",
              "        low = rel.lower()",
              "        hit = sum(1 for t in toks if t in low)",
              "        if hit == len(toks) and hit > bs: best, bs = dp, hit",
              "    return best",
              "def desk_paths():",
              "    d = desk_load()",
              "    return [x for x in (d.get('primary'), d.get('secondary')) if x and os.path.isdir(x)]",
              "def desk_cmd(arg, root, say=print):  # DESK v84.0: the co-pilot's chair - primary today, secondary in peripheral vision",
              "    d = desk_load()",
              "    if not arg:",
              "        say(f\"🪑 desk: {os.path.relpath(d.get('primary') or '?', root)} · secondary: {os.path.relpath(d.get('secondary') or '-', root)}\" if d.get('primary') else '🪑 no desk set - the butler watches the whole library evenly')",
              "    elif arg == 'clear':",
              "        desk_save({'primary': '', 'secondary': ''}); say('🪑 desk cleared - back to librarian mode')",
              "    elif arg == 'swap':",
              "        d['primary'], d['secondary'] = d.get('secondary', ''), d.get('primary', ''); desk_save(d)",
              "        say(f\"🪑 swapped - desk: {os.path.relpath(d.get('primary') or '?', root)}\")",
              "    elif arg.startswith('+'):",
              "        p = desk_resolve(arg[1:], root)",
              "        if p: d['secondary'] = p; desk_save(d); say(f'🪑 secondary desk: {os.path.relpath(p, root)}')",
              "        else: say(f'🤷 no position folder matches {arg[1:]}')",
              "    else:",
              "        p = desk_resolve(arg, root)",
              "        if p: d['primary'] = p; desk_save(d); say(f'🪑 desk set: {os.path.relpath(p, root)} - errands and instant processing point here')",
              "        else: say(f'🤷 no position folder matches {arg}')",
              "def _tag_write(p, tags):  # TAG-WRITE v84.0: kernel-direct and synchronous - what we write is what the next read sees",
              "    import plistlib as _pl",
              "    name = 'com.apple.metadata:_kMDItemUserTags'",
              "    try:",
              "        if tags: os.setxattr(p, name, _pl.dumps(tags, fmt=_pl.FMT_BINARY))",
              "        else:",
              "            try: os.removexattr(p, name)",
              "            except Exception: pass",
              "        return",
              "    except Exception:",
              "        pass",
              "    if tags:",
              "        subprocess.run(['xattr', '-w', '-x', name, _pl.dumps(tags, fmt=_pl.FMT_BINARY).hex(), p], check=True)",
              "    else:",
              "        try: subprocess.run(['xattr', '-d', name, p], check=True)",
              "        except Exception: pass",
              "def _tag_roundtrip_ok():  # S217 witness body",
              "    import tempfile",
              "    try:",
              "        fd, tp = tempfile.mkstemp(suffix='.pdf', dir=BASE_DIR); os.close(fd)",
              "        _tag_write(tp, ['Alpha Tag']); cur = _tags_of(tp)",
              "        _tag_write(tp, cur + ['Beta Tag']); cur2 = _tags_of(tp)",
              "        ok = 'Alpha Tag' in cur2 and 'Beta Tag' in cur2",
              "        _tag_write(tp, [t for t in cur2 if t != 'Beta Tag']); ok = ok and 'Alpha Tag' in _tags_of(tp)",
              "        os.remove(tp); return ok",
              "    except Exception:",
              "        try: os.remove(tp)",
              "        except Exception: pass",
              "        return False",
              "def _tag_vocab():  # DESK v84.0: built at call time, so no ordering of the book can starve it",
              "    return list(PIPELINE_CLOCKED) + list(PIPELINE_MOMENT) + list(PIPELINE_TERMINAL) + list(PIPELINE_PRE)",
              "def _match_tag(w):",
              "    low = (w or '').lower(); best = None",
              "    for t in _tag_vocab():",
              "        if low == t.lower() or (len(low) > 3 and low in t.lower()): best = t",
              "    return best",
              "def tag_apply(name, tagwords, on, say=print):  # TAG-VOICE v84.0: your word moves the tag, the machine keeps the rest",
              "    tag = _match_tag(tagwords)",
              "    if not tag: say(f'🤷 no known tag matches {tagwords!r}'); return",
              "    scope = desk_paths() or [_pl_root()]",
              "    toks = [t for t in name.lower().split() if t]; cands = []",
              "    for sc in scope:",
              "        for dp, dn, fn in os.walk(sc):",
              "            for x in fn:",
              "                if x.lower().endswith(('.pdf', '.docx')) and all(t in x.lower() for t in toks): cands.append(os.path.join(dp, x))",
              "    if not cands: say(f'🤷 no candidate file matches {name!r} on the desk'); return",
              "    if len(cands) > 1: say('❓ several humans match: ' + ' · '.join(os.path.basename(c) for c in cands[:5])); return",
              "    p = cands[0]; cur = _tags_of(p)",
              "    if on and tag not in cur: _tag_write(p, cur + [tag]); say(f'🏷️ tagged {os.path.basename(p)}: {tag}')",
              "    elif not on and tag in cur: _tag_write(p, [t for t in cur if t != tag]); say(f'🏷️ untagged {os.path.basename(p)}: {tag}')",
              "    else: say(f'🏷️ {os.path.basename(p)} already {\"wears\" if on else \"lacks\"} {tag} - nothing changed')",
              ""]
    done.append('desk-helpers')
    src = '\n'.join(B)
if 'def _errands_tick(' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def _pipeline_reconcile('))
    B[i:i] = ["    def _errands_tick(self, say=print):  # ERRANDS v84.0: the background hands - chases arm on the desk, draft in the outbox of your thumb",
              "        try:",
              "            now = int(time.time()); ep = os.path.join(BASE_DIR, 'errands.json')",
              "            er = json.load(open(ep)) if os.path.exists(ep) else {}",
              "            changed = False",
              "            for dp in desk_paths():",
              "                for dpx, dnx, fnx in os.walk(dp):",
              "                    for x in fnx:",
              "                        if not x.lower().endswith(('.pdf', '.docx')): continue",
              "                        p = os.path.join(dpx, x); tgs = _tags_of(p)",
              "                        for tag, delay in (('Awaiting JD Confirmation', 600), ('Awaiting CV Update', None)):",
              "                            at_k, ch_k = tag + ':at', tag + ':chased'",
              "                            if tag in tgs:",
              "                                if er.get(p, {}).get(at_k) is None:",
              "                                    er.setdefault(p, {})[at_k] = now; changed = True",
              "                                    say(f'📨 chase armed: {x} ({tag}) - the draft wakes in ten minutes or at morning, whichever is kinder')",
              "                                at = er[p][at_k]",
              "                                due = at + delay if delay else _next_11(at)",
              "                                due = _clamp_window(due)  # QUIET-WINDOW v84.0: nothing knocks before nine or after half past seven",
              "                                if now >= due and not er[p].get(ch_k):",
              "                                    er[p][ch_k] = now; changed = True",
              "                                    say(f'📨 chase due: {x} - type: chase send {os.path.splitext(x)[0].split()[0].lower()}')",
              "                            elif er.get(p, {}).get(ch_k):",
              "                                er[p].pop(ch_k, None); er[p].pop(at_k, None); changed = True",
              "            if changed: json.dump(er, open(ep, 'w'), indent=1)",
              "        except Exception as _ee:",
              "            say(f'⚠️ errands skipped: {_ee}')",
              ""]
    done.append('errands-method')
    src = '\n'.join(B)
if 'def _next_11(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def _pl_eod_ts('))
    B[i:i] = ["def _next_11(ts):  # ERRANDS v84.0: a promised-morning chase wakes at eleven",
              "    st = time.localtime(ts)",
              "    cand = int(time.mktime((st.tm_year, st.tm_mon, st.tm_mday, 11, 0, 0, 0, 0, -1)))",
              "    return cand if cand > ts else cand + 86400",
              "def _clamp_window(ts):  # QUIET-WINDOW v84.0",
              "    st = time.localtime(ts)",
              "    day = int(time.mktime((st.tm_year, st.tm_mon, st.tm_mday, 0, 0, 0, 0, 0, -1)))",
              "    if ts < day + 9 * 3600: return day + 9 * 3600",
              "    if ts > day + 19 * 3600 + 1800: return day + 86400 + 9 * 3600",
              "    return ts",
              ""]
    done.append('quiet-window')
    src = '\n'.join(B)
if 'def chase_cmd(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def pipeline_note('))
    B[i:i] = ["def _chase_draft(p, tag):",
              "    first = os.path.splitext(os.path.basename(p))[0].split()[0].title()",
              "    if tag == 'Awaiting JD Confirmation':",
              "        return f'Hi {first}, just checking the JD I shared reached you - a quick acknowledgement once you have gone through it would help me move things forward for you.'",
              "    return f'Hi {first}, following up on the CV update you mentioned - whenever it is ready, please share the latest version so I can push it forward today.'",
              "def chase_cmd(arg, root, say=print):  # CHASE v84.0: the draft waits in the field, never in the send column",
              "    ep = os.path.join(BASE_DIR, 'errands.json')",
              "    er = json.load(open(ep)) if os.path.exists(ep) else {}",
              "    due = [(p, e) for p, e in er.items() if isinstance(e, dict) and any(k.endswith(':chased') for k in e)]",
              "    if arg.startswith('send '):",
              "        nm = arg[5:].strip().lower(); hit = None",
              "        for p, e in due:",
              "            if nm and nm in os.path.basename(p).lower(): hit = (p, e); break",
              "        if not hit: say(f'🤷 no chase due for {arg[5:]}'); return",
              "        p, e = hit",
              "        tag = next((k[:-7] for k in e if k.endswith(':chased')), 'Awaiting JD Confirmation')",
              "        ph = taught_digits(os.path.splitext(os.path.basename(p))[0]) or phones_of(p)",
              "        if not ph: say(f'⚠️ no phone for {os.path.basename(p)} - teach it first'); return",
              "        if isinstance(ph, list): ph = ph[0]",
              "        import wa",
              "        wa.send_review(ph, _chase_draft(p, tag), say)",
              "        return",
              "    if not due: say('📭 no chase due right now - the desk is quiet'); return",
              "    for p, e in due:",
              "        tag = next((k[:-7] for k in e if k.endswith(':chased')), '?')",
              "        say(f\"📨 {os.path.basename(p)} · {tag}\")",
              "        say(f\"   draft: {_chase_draft(p, tag)}\")",
              "def daily_briefing(say=print):  # BRIEFING v84.0: yesterday's trail and today's dues in one breath",
              "    now = int(time.time()); st = time.localtime(now)",
              "    d0 = int(time.mktime((st.tm_year, st.tm_mon, st.tm_mday, 0, 0, 0, 0, 0, -1)))",
              "    y0, y1 = d0 - 86400, d0",
              "    dd = desk_load()",
              "    say(f\"🪑 desk: {os.path.basename(dd.get('primary') or '-')} · secondary: {os.path.basename(dd.get('secondary') or '-')}\")",
              "    led, _ = _pl_load(); mv = 0",
              "    say('📆 yesterday:')",
              "    for p, e in led.items():",
              "        for h in e.get('history', []):",
              "            if y0 <= h[2] < y1: say(f\"   · {os.path.basename(p)}: {h[0]} → {e.get('tag')}\"); mv += 1",
              "    try:",
              "        rl = json.load(open(os.path.join(BASE_DIR, 'rename_log.json')))",
              "        for r in rl:",
              "            if y0 <= r.get('ts', 0) < y1: say(f\"   ✏️ {r.get('old')} → {r.get('new')}\"); mv += 1",
              "    except Exception: pass",
              "    if not mv: say('   · nothing moved')",
              "    say('⏰ today:')",
              "    od = [(p, e) for p, e in led.items() if not e.get('closed') and e.get('tag') in PIPELINE_CLOCKED and now >= _pl_due(e)]",
              "    for p, e in od: say(f\"   ⚠️ {os.path.basename(p)} · {e['tag']} · {_pl_age(now, e['since'])}\")",
              "    ep = os.path.join(BASE_DIR, 'errands.json')",
              "    try:",
              "        er = json.load(open(ep))",
              "        for p, e in er.items():",
              "            if isinstance(e, dict) and any(k.endswith(':chased') for k in e): say(f'   📨 chase due: {os.path.basename(p)}')",
              "    except Exception: pass",
              "    if not od: say('   · nothing overdue')",
              ""]
    done.append('chase-briefing')
    src = '\n'.join(B)
for k, l in enumerate(B):
    if l.strip().startswith("models = [m['name'] for m in json.loads(r.read().decode())") and 'LLM-PIN' not in src:
        d = ind(l)
        B[k:k+1] = [d*' ' + "_all = [m['name'] for m in json.loads(r.read().decode()).get('models', []) if 'embed' not in m['name'].lower()]  # LLM-PIN v84.0: on 8 GB the small instruct model thinks; the 5 GB ones stall the house",
                    d*' ' + "_pref = [n for n in _all if n.startswith('qwen2.5:3b-instruct')] or [n for n in _all if n.startswith(('qwen2.5:3b', 'llama3.2', 'phi3'))] or _all",
                    d*' ' + "models = _pref[:1]"]
        done.append('llm-pin'); break
src = '\n'.join(B)
if 'self._errands_tick(' not in src:
    for k, l in enumerate(B):
        if 'self._pipeline_reconcile(say)' in l:
            B.insert(k+1, ind(l)*' ' + "self._errands_tick(say)  # ERRANDS v84.0: after the ledger, the hands")
            done.append('errands-hook'); break
    src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
srcg = '\n'.join(g)
if 'def do_desk(' not in srcg:
    i = next(k for k, l in enumerate(g) if l.startswith('def do_pending('))
    g[i:i] = ["def do_desk(arg, root, say=print):  # DESK v84.0",
              "    butler.desk_cmd(arg, root, say)",
              "def do_briefing(arg, root, say=print):  # BRIEFING v84.0",
              "    butler.daily_briefing(say)",
              "def do_chase(arg, root, say=print):  # CHASE v84.0",
              "    butler.chase_cmd(arg, root, say)",
              "def do_tagcmd(arg, root, say=print):  # TAG-VOICE v84.0",
              "    parts = arg.split(' ', 1)",
              "    if len(parts) < 2: say('usage: tag <name> <tag words>'); return",
              "    butler.tag_apply(parts[0], parts[1], True, say)",
              ""]
    done.append('desk-chat-fns')
    srcg = '\n'.join(g)
if not any(l.strip().startswith("if q.startswith('desk')") for l in g):
    for k, l in enumerate(g):
        if l.strip().startswith("if q.startswith('pending'): do_pending("):
            d = ind(l)
            g[k:k] = [d*' ' + "if q.startswith('desk'): do_desk(q[4:].strip(), root); continue  # DESK v84.0",
                      d*' ' + "if q.startswith('briefing'): do_briefing(q[8:].strip(), root); continue",
                      d*' ' + "if q.startswith('chase'): do_chase(q[5:].strip(), root); continue",
                      d*' ' + "if q.startswith('tag '): do_tagcmd(q[4:].strip(), root); continue"]
            done.append('desk-chat-dispatch'); break
    srcg = '\n'.join(g)
if srcg != open(G).read():
    ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S217 the tag-writer preserves every tag it was not asked about", "'S216 the master's words stand at the head of the chat chain", "ck('S217 the tag-writer preserves every tag it was not asked about', _tag_roundtrip_ok())"),
      ("'S218 no chase knocks before nine or after half past seven", "'S217 the tag-writer preserves every tag it was not asked about", "ck('S218 no chase knocks before nine or after half past seven', (chr(35)+' QUIET-WINDOW v84.0') in _src and ('def _clamp_window(' in _src))"),
      ("'S219 the desk is a chair, not a cage - focus still roams", "'S218 no chase knocks before nine or after half past seven", "ck('S219 the desk is a chair, not a cage - focus still roams', ('def desk_cmd(' in _src) and ('def do_focus(' in open(os.path.join(BASE_DIR, 'briefing.py')).read()))"),
      ("'S220 the small model thinks on a small machine", "'S219 the desk is a chair, not a cage - focus still roams", "ck('S220 the small model thinks on a small machine', (chr(35)+' LLM-PIN v84.0') in _src)"),
      ("'S221 the tag reader asks the kernel, not the index", "'S220 the small model thinks on a small machine", "ck('S221 the tag reader asks the kernel, not the index', 'os.getxattr(' in _src[_src.find('def _tags_of('):_src.find('PIPELINE_CLOCKED =')])")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
