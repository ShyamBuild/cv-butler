import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
F = open('briefing.py').read()
if 'def _split_pos(' not in F:
    helper = '''CITY_WORDS = ['greater noida', 'vikhroli east', 'vikhroli', 'mumbai', 'bengaluru', 'bangalore', 'delhi', 'gurugram', 'gurgaon', 'noida', 'pune', 'chennai', 'hyderabad', 'ahmedabad', 'kolkata', 'jaipur', 'lucknow', 'indore', 'nagpur', 'thane', 'erode', 'coimbatore']
def _split_pos(pos):
    low = (pos or '').lower(); locs = []
    for c in CITY_WORDS:
        if c in low:
            locs.append(c.title()); low = low.replace(c, ' ')
    title = re.sub(r'\\s+', ' ', low).strip(' -|,')
    seen = []
    for x in locs:
        if x not in seen: seen.append(x)
    return ((title.title() if title else pos), ', '.join(seen))
def _fmt_tpl(tpl, hit, f, name):
    pos, cli = _pos_client_for(hit, f)
    title, loc = _split_pos(pos)
    where = f"Company: {cli}" + (f" | Location: {loc}" if loc else "")
    try:
        return tpl.format(name=name, position=title, company=cli, location=loc or '-', where_line=where)
    except Exception:
        return tpl
'''
    i = F.index('def _pos_client_for(hit, f=None):')
    F = F[:i] + helper + F[i:]
    done.append('split-pos-fmt-tpl')
old = "    head = (_jd_text_for(pos_path) or '')[:600]"
if old in F and 'filename-first seed' not in F:
    seed = ("    # filename-first seed v49\n"
            "    try:\n"
            "        for fn in os.listdir(pos_path):\n"
            "            lf = fn.lower()\n"
            "            if lf.startswith('jd') or '_jd' in lf or ' jd' in lf or lf.endswith(('.eml', '.msg')):\n"
            "                m = re.match(r'^(?:jd|fw|fwd)[\\s_\\-:]*(.{2,40}?)(?:\\s*[-–_|]|\\.pdf|\\.eml|\\.msg)', fn, re.I)\n"
            "                if m:\n"
            "                    w = m.group(1).strip().split()\n"
            "                    if w and len(w[0]) > 3: w[0] = w[0].title()\n"
            "                    return ' '.join(w[:4])\n"
            "    except Exception:\n"
            "        pass\n")
    F = F.replace(old, seed + old, 1); done.append('client-seed-filename-first')
repl = [("_tpl_for(['missed']).format(name=nm, position=pos, company=cli)", "_fmt_tpl(_tpl_for(['missed']), None, f, nm)"),
        ("_tpl_for(['missed']).format(name=name, position=_pos_client_for(hit, f)[0], company=_pos_client_for(hit, f)[1])", "_fmt_tpl(_tpl_for(['missed']), hit, f, name)"),
        ("_tpl_for(tpl_words).format(name=nm, position=pos, company=cli)", "_fmt_tpl(_tpl_for(tpl_words), None, f, nm)"),
        ("tpl.format(name=nm, position=pos, company=cli)", "_fmt_tpl(tpl, hit, f, nm)"),
        ("tpl.format(name=name, position=_pos_client_for(hit, f)[0], company=_pos_client_for(hit, f)[1])", "_fmt_tpl(tpl, hit, f, name)"),
        ("tpl.format(name=name, position=pos, company=client)", "_fmt_tpl(tpl, os.path.join(folder, x), f, name)")]
for a, b in repl:
    if a in F:
        F = F.replace(a, b); done.append('fmt-site')
if 'DEFAULT_TPL = (' in F and 'reconnect. Thanks!")' not in F:
    i = F.index('DEFAULT_TPL = (')
    j = F.index('Sunsoft Technology")', i) + len('Sunsoft Technology")')
    F = F[:i] + ('DEFAULT_TPL = ("Hi {name}, Sundeep Rana (Sunsoft Technology) - tried calling you today.\\n"\n'
                 '"Regarding the {position} role | {where_line}.\\n"\n'
                 '"Please share your updated CV (PDF) here + a good time to reconnect. Thanks!")') + F[j:]
    done.append('default-tpl-short')
open('briefing.py', 'w').write(F); ast.parse(F)
TPL = ("Hi {name}, Sundeep Rana (Sunsoft Technology) - tried calling you today.\n"
       "Regarding the {position} role | {where_line}.\n"
       "Please share your updated CV (PDF) here + a good time to reconnect. Thanks!\n")
open('wa_template.txt', 'w').write(TPL); done.append('wa-template-short')
if os.path.exists('clients.json'):
    os.replace('clients.json', 'clients.json.bak'); done.append('clients-reseed-backup')
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if l.strip().startswith("ck('S51 drafts use position/client truth'"):
        B[k] = ind(l)*' ' + "ck('S51 drafts use position/client truth', 'def _pos_client_for(' in _br and 'def _fmt_tpl(' in _br and \"position=f['display']\" not in _br)"
        done.append('S51-evolved'); break
if "'S53 professional template" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S52 client alias command routed" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "_tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wa_template.txt')).read() if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wa_template.txt')) else ''")
    B.insert(i+2, d*' ' + "ck('S53 professional template live', 'Sundeep Rana' in _tpl and '{where_line}' in _tpl)")
    B.insert(i+3, d*' ' + "ck('S54 position/location split wired', 'def _split_pos(' in _br and 'def _fmt_tpl(' in _br)")
    done.append('S53-S54-guards')
open('butler.py', 'w').write('\n'.join(B))
print('✅', done)
