import ast, re
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'def _names_by_phone(' not in src:
    i = next(k for k, l in enumerate(B) if l.startswith('def _sniff_ext('))
    B[i:i] = ["def _names_by_phone():",
              "    try:",
              "        import json as _j",
              "        return _j.load(open(os.path.join(BASE_DIR, 'names_by_phone.json')))",
              "    except Exception:",
              "        return {}",
              ""]
    done.append('names-by-phone-helper')
m = re.search(r"def handle_pdf\(.*?phones_of\((\w+)\)", '\n'.join(B), re.S)
arg = m.group(1) if m else 'hay'
src = '\n'.join(B)
if '# NAME-BY-PHONE v79' not in src:
    i = next(k for k, l in enumerate(B) if '# SUFFIX-STABLE v65' in l)
    d = ind(B[i])
    B[i:i] = [d*' ' + f"_nbm = _names_by_phone()  # NAME-BY-PHONE v79",
              d*' ' + "_nb = ''",
              d*' ' + f"for _d in (phones_of({arg}) or []):",
              d*' ' + "    if _d in _nbm: _nb = _nbm[_d]; break",
              d*' ' + "if _nb: name = _nb"]
    done.append('handle-pdf-prefers-learned')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
F = open('briefing.py').read().split('\n')
if 'def do_name(' not in '\n'.join(F):
    i = next(k for k, l in enumerate(F) if l.strip().startswith('def do_renwhy('))
    F[i:i] = ["def do_name(arg, root, say=print):",
              "    import json, re as _re, time, fitrank, butler as _bt",
              "    parts = (arg or '').strip().split(None, 1)",
              "    if len(parts) < 2: say('usage: name <phone-or-fileword> <Correct Name>'); return",
              "    dig = _re.sub(r'\\D', '', parts[0]); nm = parts[1].strip()",
              "    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'names_by_phone.json')",
              "    m = {}",
              "    try: m = json.load(open(p))",
              "    except Exception: pass",
              "    m[dig] = nm",
              "    json.dump(m, open(p, 'w'), indent=1)",
              "    say(f'📇 learned: {dig} -> {nm}')",
              "    for dp, dn, fn in os.walk(root):",
              "        dn[:] = [d for d in dn if not d.startswith('.')]",
              "        for f in fn:",
              "            if not f.lower().endswith('.pdf'): continue",
              "            fp = os.path.join(dp, f)",
              "            try:",
              "                if time.time() - os.stat(fp).st_mtime < 20: continue",
              "                if dig not in (_bt.phones_of(fitrank._text(fp)) or []): continue",
              "                d0 = os.path.dirname(fp); b, e = os.path.splitext(f)",
              "                tgt = os.path.join(d0, nm + e); c = 1",
              "                while os.path.exists(tgt): tgt = os.path.join(d0, f'{nm}_{c}{e}'); c += 1",
              "                if tgt != fp: os.rename(fp, tgt); say(f'✏️ [rename] {f} -> {os.path.basename(tgt)}')",
              "            except Exception: pass",
              ""]
    done.append('name-command')
for k, l in enumerate(F):
    if "'refer','renwhy')" in l and "'name'" not in l:
        F[k] = l.replace("'renwhy')", "'renwhy','name')"); done.append('door-list'); break
for k, l in enumerate(F):
    if l.strip().startswith("elif cmd == 'renwhy'"):
        F.insert(k+1, ind(l)*' ' + "elif cmd == 'name': do_name(arg, root, print)")
        done.append('cli-name'); break
for k, l in enumerate(F):
    if l.strip().startswith("if q.lower().startswith('renwhy ')"):
        F.insert(k+1, ind(l)*' ' + "if q.lower().startswith('name '): do_name(q[5:].strip(), root); continue")
        done.append('chat-name'); break
new = '\n'.join(F); ast.parse(new); open('briefing.py', 'w').write(new)
B = open('butler.py').read().split('\n')
if "'S101 learned names beat document names" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S100 tag-truth is the only filing voice" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S101 learned names beat document names', 'def _names_by_phone(' in _src and (chr(35)+' NAME-BY-PHONE') in _src)")
    B.insert(i+2, d*' ' + "ck('S102 name command learns and renames on demand', 'def do_name(' in _br and \"cmd == 'name'\" in _br)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S101-S102-guards')
print('✅', done)
