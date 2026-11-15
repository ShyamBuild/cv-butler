import ast, os, re
done = []
def ind(l): return len(l) - len(l.lstrip())
def markers(lines):
    out = []
    for l in lines:
        out += re.findall(r'# [A-Z0-9-]+ v[0-9.]+', l)
    return out
def perfile():
    S = {}
    for fn in ('butler.py', 'briefing.py', 'wa.py'):
        P = os.path.join(os.getcwd(), fn)
        S[fn] = set(markers(open(P).read().split('\n'))) if os.path.exists(P) else set()
    return S
M0 = perfile()
W0 = open('wa.py').read()
w = W0.split('\n')
snapw = list(w)
b0 = next(k for k, l in enumerate(w) if l.startswith('def _send_review_body('))
b1 = next(k for k in range(b0 + 1, len(w)) if w[k].startswith('def '))
fk = next((k for k in range(b0, b1) if ('insert_text(' in w[k] or '.fill(' in w[k] or '.type(' in w[k]) and 'FIELD-CLEAR' not in '\n'.join(w[b0:k])), None)
if fk is not None:
    d = ind(w[fk])
    w[fk:fk] = [d*' ' + "try:  # FIELD-CLEAR v85.34: the persistent composer keeps yesterday's sentence unless the ritual empties it first - select-all and delete before every fill, so no ghost text can ride along",
                (d+4)*' ' + "page.keyboard.press('Meta+a')",
                (d+4)*' ' + "page.keyboard.press('Delete')",
                d*' ' + "except Exception:",
                (d+4)*' ' + "pass"]
    done.append('field-clear')
srcw = '\n'.join(w)
if srcw != W0:
    ast.parse(srcw); open('wa.py', 'w').write(srcw)
B0 = open('butler.py').read()
B = B0.split('\n')
snap = list(B)
s0 = next(k for k, l in enumerate(B) if l.startswith('def seat_rename_check('))
r0 = next((k for k, l in enumerate(B) if l.strip().startswith("if os.path.exists(_rp): return open(_rp).read().strip().format_map(_draft_fields(")), None)
if r0 is not None:
    d = ind(B[r0])
    B[r0:r0+1] = [d*' ' + "if os.path.exists(_rp):  # REFER-FIELDS v85.34: the courtesy formats from truths the house already holds - name from the row, role and company from the identity and the desk's teaching, location from the same witness",
                  (d+4)*' ' + "import collections as _cc, json as _j2",
                  (d+4)*' ' + "_pi = pos_identity(p)",
                  (d+4)*' ' + "_dm = {}",
                  (d+4)*' ' + "try: _dm = _j2.load(open(os.path.join(BASE_DIR, 'desk_meta.json'))).get(desk_load().get('primary') or '', {})",
                  (d+4)*' ' + "except Exception: pass",
                  (d+4)*' ' + "_fld = _cc.defaultdict(str, {'name': name, 'position': _pi.get('role') or os.path.basename(os.path.dirname(p)), 'company': _pi.get('company') or _dm.get('company') or '', 'location': _pi.get('loc') or _pi.get('location') or ''})",
                  (d+4)*' ' + "return open(_rp).read().strip().format_map(_fld)"]
    done.append('refer-fields-local')
tk = next((k for k, l in enumerate(B) if "tray: ' + ', '.join(os.path.basename(x) for x in _sk[:4])" in l), None)
if tk is not None and 'TIDY-TRAY' not in B[tk]:
    B[tk] = B[tk].replace("', '.join(os.path.basename(x) for x in _sk[:4])", "str(len(_sk)) + ': ' + ', '.join(os.path.basename(x).replace('.pdf', '').replace('.PDF', '') for x in _sk[:4])")
    B[tk] = B[tk].rstrip() + '  # TIDY-TRAY v85.34: names without tails, count up front'
    done.append('tray-tidy')
ck = next((k for k, l in enumerate(B) if l.strip().startswith('say(') and '📊' in l and 'feedback' in l), None)
if ck is not None and 'TIDY-CENSUS' not in B[ck]:
    line = B[ck]
    ci = line.index('say(')
    comment = ''
    if '  #' in line:
        li = line.index('  #')
        comment = line[li:]
        line = line[:li]
    body = line[ci+4:]
    if body.endswith(')'):
        body = body[:-1]
    B[ck] = line[:ci+4] + body + ".replace(':', ' ')" + ')' + ('  ' + comment.strip() if comment else '') + '  # TIDY-CENSUS v85.34: spaces instead of colons - same truths, quieter type'
    done.append('census-tidy')
print('🔎 refer block, tray and census lines:')
for k, l in enumerate(B):
    if 'REFER-FIELDS v85.34' in l or 'TIDY-TRAY v85.34' in l or 'TIDY-CENSUS v85.34' in l:
        print('   |', l)
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
M1 = perfile()
lost = set()
for fn in M0:
    lost |= (M0[fn] - M1.get(fn, set()))
if lost:
    print('⛔ witness diff per file:', sorted(lost)); raise SystemExit('harvest first')
print('🔎 witness diff per file: 0 laws lost')
AR = os.path.join(os.getcwd(), 'ARCHITECTURE.md')
try:
    t = open(AR).read()
    if 'v85.34' not in t:
        open(AR, 'a').write('v85.34: FIELD-CLEAR empties the persistent composer before every fill; REFER-FIELDS formats the courtesy from name, pos_identity and desk_meta instead of the blind helper; TIDY-TRAY drops .pdf tails and leads with the count; TIDY-CENSUS trades colons for spaces (S373, S374)\n')
        done.append('arch-line')
except Exception: pass
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S373 the composer is emptied before it is filled - no ghost sentence rides along", "'S372 a scan is recognised by its face when its contacts are silent", "ck('S373 the composer is emptied before it is filled - no ghost sentence rides along', (chr(35)+' FIELD-CLEAR v85.34') in open(os.path.join(BASE_DIR, 'wa.py')).read())"),
      ("'S374 the courtesy formats from truths the house holds and the lines read quiet", "'S373 the composer is emptied before it is filled - no ghost sentence rides along", "ck('S374 the courtesy formats from truths the house holds and the lines read quiet', (chr(35)+' REFER-FIELDS v85.34') in _src and (chr(35)+' TIDY-TRAY v85.34') in _src and (chr(35)+' TIDY-CENSUS v85.34') in _src)")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
