import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
i0 = next(k for k, l in enumerate(g) if l.startswith('def _fmt_tpl('))
i1 = next(k for k in range(i0 + 1, len(g)) if g[k].startswith('def _pos_client_for('))
if 'def _tpl_fields(' not in '\n'.join(g[i0:i1]):
    g[i0:i1] = ["def _tpl_fields(hit, f, name):  # DRAFT-WHY v84.33: one place computes every field, so every door and every explanation agree",
                "    pos, cli = _pos_client_for(hit, f)",
                "    title, loc = _split_pos(pos)",
                "    _dz = ''",
                "    try:",
                "        import butler as _bt",
                "        _idn = _bt.pos_identity(str(hit)) if (hit and os.path.isfile(str(hit))) else {}",
                "        if _idn.get('company'): cli = _idn['company']",
                "        if _idn.get('role'): title = _idn['role']",
                "        if _idn.get('loc'): loc = _idn['loc']",
                "        _dz = _idn.get('designation') or title",
                "    except Exception:",
                "        _dz = _dz or title",
                "    where = f\"Company: {cli}\" + (f\" | Location: {loc}\" if loc else \"\")",
                "    at = cli + (f\", {loc}\" if loc else \"\")",
                "    return {'name': name, 'position': title, 'company': cli, 'location': loc or '-', 'where_line': where, 'where': at, 'designation': _dz}",
                "def _fmt_tpl(tpl, hit, f, name):",
                "    try:  # POS-ID v84.21: every draft, keyword or chair, shows the position's triple before the window opens",
                "        if hit and os.path.isfile(str(hit)):",
                "            import butler as _bt; _bt.say_identity_for(str(hit), print)",
                "    except Exception: pass",
                "    fld = _tpl_fields(hit, f, name)",
                "    try:",
                "        return tpl.format(**fld)",
                "    except Exception:",
                "        return tpl.format_map(_SafeDict(**fld))",
                ""]
    done.append('tpl-fields')
srcg = '\n'.join(g)
if 'def do_draftwhy(' not in srcg:
    i = next(k for k, l in enumerate(g) if l.startswith('def do_adlog('))
    TDIR = "os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')"
    g[i:i] = ["def do_draftwhy(arg, root, say=print):  # DRAFT-WHY v84.33: eyes behind every draft - which guess, which truth, which fields, which files",
              "    hits = _hits_for((arg or '').strip(), root)",
              "    if not hits: say(f'🤷 no CV matches {arg!r}'); return",
              "    p = hits[0]; nm = os.path.splitext(os.path.basename(p))[0]",
              "    pos, cli = _pos_client_for(p, None); title, loc = _split_pos(pos)",
              "    import butler as _bt",
              "    idn = _bt.pos_identity(p)",
              "    say(f'🔎 draft anatomy for {nm}:')",
              "    say(f'   legacy path-guess : position={title!r} company={cli!r} location={loc!r}')",
              "    say(f'   registry truth    : company={idn.get(chr(39)+chr(39)) or idn.get(\"company\")!r} role={idn.get(\"role\")!r} loc={idn.get(\"loc\")!r} designation={idn.get(\"designation\")!r}')",
              "    fld = _tpl_fields(p, None, nm)",
              "    say('   fields used       : ' + ' · '.join(f'{k}={v!r}' for k, v in fld.items()))",
              "    TDIR = " + TDIR,
              "    for w in ('jd', 'missed', 'nudge', 'refer', 'awaiting'):",
              "        try: cands = [fn for fn in sorted(os.listdir(TDIR)) if fn.endswith('.txt') and w in fn.lower()]",
              "        except Exception: cands = []",
              "        say(f'   scenario {w} files : ' + (', '.join(cands[:4]) or 'none'))",
              "    say('   rendered jd draft :')",
              "    for ln in _fmt_tpl(_tpl_for(['jd']), p, None, nm).split(chr(10)): say('     ' + ln)",
              "    say('   queued chases     : ad_wait.py build_text composes them - v84.34 brings it to this same composer')",
              ""]
    done.append('draftwhy')
    srcg = '\n'.join(g)
if 'draftwhy' not in srcg.split('def do_draftwhy')[0].split('\n')[-1] and not any(l.strip().startswith("if q.startswith('draftwhy')") for l in g):
    for k, l in enumerate(g):
        if l.strip().startswith("if q.strip() == 'refresh':"):
            d = ind(l)
            g.insert(k, d*' ' + "if q.startswith('draftwhy '): do_draftwhy(q[9:].strip(), root, say); continue  # DRAFT-WHY v84.33")
            done.append('chat-draftwhy'); break
    srcg = '\n'.join(g)
if srcg != open(G).read():
    ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if "'clients', 'refresh', 'options')" in l and 'draftwhy' not in l:
        B[k] = l.replace("'options')", "'options', 'draftwhy')")
        done.append('cli-tuple')
for k, l in enumerate(B):
    if l.strip().startswith("elif _v == 'options':") and 'draftwhy' not in '\n'.join(B[k:k+3]):
        d = ind(l)
        B.insert(k+1, d*' ' + "elif _v == 'draftwhy': import briefing as _br; _br.do_draftwhy(' '.join(_a), _pl_root(), print)")
        done.append('cli-draftwhy'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S295 every draft can name its guesses, its truths, its fields and its files", "'S294 widening a tuple never amputates its marker", "ck('S295 every draft can name its guesses, its truths, its fields and its files', (chr(35)+' DRAFT-WHY v84.33') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and ('def _tpl_fields(' in open(os.path.join(BASE_DIR, 'briefing.py')).read()) and ('def do_draftwhy(' in open(os.path.join(BASE_DIR, 'briefing.py')).read()))")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
