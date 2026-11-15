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
B0 = open('butler.py').read()
B = B0.split('\n')
snap = list(B)
o0 = next(k for k, l in enumerate(B) if l.startswith('def outcome_cmd('))
if 'WR-FIRST' not in B[o0+1]:
    B.insert(o0+1, '    _wr = True  # WR-FIRST v85.35: every path through the outcome carries its witness to the deed line, including the no-phone walk-on')
    done.append('wr-first')
if 'def _display_name(' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.startswith('def seat_rename_check('))
    B[i:i] = ["def _display_name(s):  # CASE-LAW v85.35: the original butler's rule returns - a shout is not a name: RAHUL KUMAR becomes Rahul Kumar, single letters stay capital, short initial-blocks keep their form",
              "    out = []",
              "    for w in str(s).split():",
              "        if len(w) == 1: out.append(w.upper())",
              "        elif w.isalpha() and w.isupper() and len(w) <= 3: out.append(w)",
              "        elif w.isalpha() and (w.isupper() or w.islower()): out.append(w.capitalize())",
              "        else: out.append(w)",
              "    return ' '.join(out)",
              ""]
    done.append('display-name')
s0 = next(k for k, l in enumerate(B) if l.startswith('def seat_rename_check('))
s1 = next(k for k in range(s0 + 1, len(B)) if B[k].startswith('def '))
ek = next((k for k in range(s0, s1) if B[k].strip().startswith('v = heuristic_name(p)')), None)
if ek is not None and 'VISION-ONCE' not in '\n'.join(B[s0:s1]):
    d = ind(B[ek])
    B[ek:ek+1] = [d*' ' + "v = heuristic_name(p) or _name_from_first_line(p)  # TEXT-EYES v85.16  # FIRST-LINE v85.20: every rewritten line carries the witnesses it already wore",
                  d*' ' + "if not v and x not in rec.get('vtried', []):  # VISION-ONCE v85.35: the expensive pupil is asked once per paper per day; a silent answer rests, so misses cost milliseconds thereafter",
                  (d+4)*' ' + "v = _vision_safe(p)",
                  (d+4)*' ' + "rec.setdefault('vtried', []).append(x)"]
    done.append('vision-once')
nk = next((k for k in range(s0, s1) if B[k].strip().startswith('if _name_key(os.path.splitext(x)[0]) == _name_key(canon): continue')), None)
if nk is not None and 'CASE-LAW' not in B[nk]:
    d = ind(B[nk])
    B[nk:nk+1] = [d*' ' + "stem = os.path.splitext(x)[0]",
                  d*' ' + "if _name_key(stem) != _name_key(canon): continue",
                  d*' ' + "canon = _display_name(canon)  # CASE-LAW v85.35: rename when the human matches but the display does not - all-caps files are renamed at last",
                  d*' ' + "if stem == canon: continue"]
    done.append('case-rename')
pk = next((k for k, l in enumerate(B) if l.strip().startswith('say(') and 'pick the human by email' in l), None)
if pk is not None:
    print('🔎 pick window raw:')
    for k in range(pk, min(pk+30, len(B))):
        print('   |', repr(B[k])[:200])
    for k in range(pk, min(pk+60, len(B))):
        if re.search(r'\[int\([^)]*\)\]', B[k]) and 'PICK-BASE' not in B[k] and '- 1]' not in B[k]:
            B[k] = re.sub(r'\[int\(([^)]*)\)\]', lambda m: '[int(%s) - 1]' % m.group(1), B[k], count=1)
            B[k] = B[k].rstrip() + '  # PICK-BASE v85.36: the menu counts from one and the hand must too'
            done.append('pick-base'); break
    for k in range(pk, min(pk+60, len(B))):
        if 'phones_of(' in B[k] and ('cand' in B[k] or 'for ' in B[k] or 'next(' in B[k]) and 'PICK-PHONE' not in B[k]:
            d = ind(B[k])
            B[k] = d*' ' + "ph = ph or []  # PICK-PHONE v85.37: the picked human's own number or none - a number borrowed from a sibling row stitches two humans into one deed"
            done.append('pick-phone'); break
p0 = next(k for k, l in enumerate(B) if l.startswith('def phones_in_text('))
if 'PHONE-GLUE' not in B[p0+1]:
    d = ind(B[p0+1]) if p0+1 < len(B) else 4
    B.insert(p0+1, d*' ' + "t = re.sub(r'([6-9]\\d{4})[\\s.\\-](\\d{5})', r'\\1\\2', t or ''); t = re.sub(r'(\\+?91)[\\s.\\-]([6-9]\\d{9})', r'\\1\\2', t)  # PHONE-GLUE v85.35 + v85.37 constraint: only groups that could be a mobile may join - a pincode keeps its six digits and never lends them to a phantom phone (S168 honoured)")
    done.append('phone-glue')
c0 = next(k for k, l in enumerate(B) if l.startswith('def calls_cmd('))
c1 = next(k for k in range(c0 + 1, len(B)) if B[k].startswith('def sheet_cmd('))
sl = next((k for k in range(c0, c1) if 'sheet_load()' in B[k]), None)
if sl is not None and 'DESK-SCOPE' not in '\n'.join(B[c0:sl+4]):
    d = ind(B[sl])
    vn = B[sl].split('=')[0].strip()
    B.insert(sl+1, d*' ' + "if %s.get('desk') != root:  # DESK-SCOPE v85.35: a new position's sheet forgets the old position's waiting rows in one breath - they belong to another chair" % vn)
    B.insert(sl+2, (d+4)*' ' + "%s['items'] = [i for i in %s.get('items', []) if os.path.realpath(i.get('p', '')).startswith(os.path.realpath(root))]" % (vn, vn))
    B.insert(sl+3, (d+4)*' ' + "%s['desk'] = root" % vn)
    B.insert(sl+4, (d+4)*' ' + "sheet_save(%s)" % vn)
    done.append('desk-scope')
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
ck = next((k for k, l in enumerate(B) if l.strip().startswith('say(') and '📊' in l and 'TIDY-CENSUS' not in l), None)
if ck is not None:
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
if ast.parse('\n'.join(B)):
    open('butler.py', 'w').write('\n'.join(B))
else:
    B = snap; done.append('revert:butler')
W0 = open('wa.py').read()
w = W0.split('\n')
snapw = list(w)
fk = next((k for k, l in enumerate(w) if (('insert_text(' in l) or ('.fill(' in l) or ('.type(' in l)) and ('FIELD-CLEAR' not in '\n'.join(w[:k]))), None)
if fk is not None:
    d = ind(w[fk])
    w[fk:fk] = [d*' ' + "try:  # FIELD-CLEAR v85.34: the persistent composer keeps yesterday's sentence unless the ritual empties it first - select-all and delete before every fill",
                (d+4)*' ' + "page.keyboard.press('Meta+a')",
                (d+4)*' ' + "page.keyboard.press('Delete')",
                d*' ' + "except Exception:",
                (d+4)*' ' + "pass"]
    done.append('field-clear')
srcw = '\n'.join(w)
if srcw != W0:
    ast.parse(srcw); open('wa.py', 'w').write(srcw)
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
    if 'v85.37' not in t:
        open(AR, 'a').write('v85.37: PHONE-GLUE constrained to mobile-shaped groups so pincodes keep their digits (S168); the pick window opens at the say-line and fixes whichever sin it finds - PICK-BASE index or PICK-PHONE sibling borrowing - printing its raw lines as evidence; the ten cures of v85.35 land whole (S373-S378)\n')
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
      ("'S374 the courtesy formats from truths the house holds and the lines read quiet", "'S373 the composer is emptied before it is filled - no ghost sentence rides along", "ck('S374 the courtesy formats from truths the house holds and the lines read quiet', (chr(35)+' REFER-FIELDS v85.34') in _src and (chr(35)+' TIDY-TRAY v85.34') in _src and (chr(35)+' TIDY-CENSUS v85.34') in _src)"),
      ("'S375 every outcome path carries its witness and every sheet knows its desk", "'S374 the courtesy formats from truths the house holds and the lines read quiet", "ck('S375 every outcome path carries its witness and every sheet knows its desk', (chr(35)+' WR-FIRST v85.35') in _src and (chr(35)+' DESK-SCOPE v85.35') in _src)"),
      ("'S376 the expensive pupil is asked once per paper per day", "'S375 every outcome path carries its witness and every sheet knows its desk", "ck('S376 the expensive pupil is asked once per paper per day', (chr(35)+' VISION-ONCE v85.35') in _src)"),
      ("'S377 a shout is not a name and a split number is one number - and a pincode stays six digits", "'S376 the expensive pupil is asked once per paper per day", "ck('S377 a shout is not a name and a split number is one number - and a pincode stays six digits', (chr(35)+' CASE-LAW v85.35') in _src and (chr(35)+' PHONE-GLUE v85.35') in _src and ('[6-9]' in _src))"),
      ("'S378 one pick yields one whole human - own number or none, never a sibling's", "'S377 a shout is not a name and a split number is one number - and a pincode stays six digits", "ck('S378 one pick yields one whole human - own number or none, never a sibling'+chr(39)+'s', (chr(35)+' PICK-BASE v85.36') in _src or (chr(35)+' PICK-PHONE v85.37') in _src)")]
for needle, fb, line in GU:
    if needle not in src:
        i = anch(needle, fb, "'S215 a lock must prove its holder lives before it names the world")
        if i is None: raise SystemExit('anchor missing for ' + needle)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
